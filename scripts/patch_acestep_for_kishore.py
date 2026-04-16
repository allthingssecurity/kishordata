#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


TRAINER_IMPORT_NEEDLE = "import os\n"
TRAINER_BLOCK_START = "    def training_step(self, batch, batch_idx):\n"
TRAINER_BLOCK_END = "\n    @torch.no_grad()\n"


TRAINER_REPLACEMENT = """    def training_step(self, batch, batch_idx):
        return self.run_step(batch, batch_idx)

    def on_train_batch_end(self, outputs, batch, batch_idx):
        if not self.trainer.is_global_zero:
            return
        step = int(self.global_step)
        if step <= 0 or step % self.save_every_steps != 0:
            return
        log_dir = getattr(self.logger, "log_dir", None)
        if not log_dir:
            return
        checkpoint_root = os.path.join(log_dir, "checkpoints")
        os.makedirs(checkpoint_root, exist_ok=True)
        checkpoint_name = f"epoch={self.current_epoch}-step={step}_lora"
        checkpoint_dir = os.path.join(checkpoint_root, checkpoint_name)
        complete_flag = os.path.join(checkpoint_dir, ".complete")
        if os.path.exists(complete_flag):
            return
        tmp_dir = checkpoint_dir + ".tmp"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        if os.path.exists(checkpoint_dir):
            shutil.rmtree(checkpoint_dir)
        os.makedirs(tmp_dir, exist_ok=True)
        self.transformers.save_lora_adapter(tmp_dir, adapter_name=self.adapter_name)
        os.rename(tmp_dir, checkpoint_dir)
        with open(complete_flag, "w") as f:
            f.write("ok\\n")

        keep = []
        for name in sorted(os.listdir(checkpoint_root)):
            full = os.path.join(checkpoint_root, name)
            if os.path.isdir(full) and name.endswith("_lora"):
                keep.append(full)
        if len(keep) > self.keep_last_checkpoints:
            for old_dir in keep[:-self.keep_last_checkpoints]:
                shutil.rmtree(old_dir, ignore_errors=True)

        self.print(f"Saved LoRA-only checkpoint: {checkpoint_dir}")

    def on_save_checkpoint(self, checkpoint):
        return {}
"""


RUN_TRAIN_TEMPLATE = """from datetime import datetime
from pathlib import Path

from pytorch_lightning import Trainer
from pytorch_lightning.loggers import TensorBoardLogger

from trainer import Pipeline


DATASET_PATH = "{dataset_path}"
CHECKPOINT_DIR = "{checkpoint_dir}"
RESUME_LORA = "{resume_lora}"
ADAPTER_NAME = "{adapter_name}"
MAX_STEPS = {max_steps}
SAVE_EVERY_STEPS = {save_every_steps}
KEEP_LAST = {keep_last}
LOG_DIR = "{log_dir}"


def build_model():
    model = Pipeline(
        learning_rate=1e-4,
        num_workers=0,
        shift=3.0,
        max_steps=MAX_STEPS,
        every_plot_step=100000000,
        dataset_path=DATASET_PATH,
        checkpoint_dir=CHECKPOINT_DIR,
        adapter_name=ADAPTER_NAME,
        lora_config_path="config/zh_rap_lora_config.json",
    )
    model.save_every_steps = SAVE_EVERY_STEPS
    model.keep_last_checkpoints = KEEP_LAST
    if RESUME_LORA:
        if hasattr(model.transformers, "delete_adapters"):
            try:
                model.transformers.delete_adapters(model.adapter_name)
            except Exception:
                pass
        model.transformers.load_lora_adapter(
            RESUME_LORA,
            prefix=None,
            adapter_name=model.adapter_name,
            weight_name="pytorch_lora_weights.safetensors",
        )
        if hasattr(model.transformers, "set_adapter"):
            model.transformers.set_adapter(model.adapter_name)
        if hasattr(model.transformers, "enable_adapters"):
            model.transformers.enable_adapters()
    return model


def main():
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
    model = build_model()
    logger = TensorBoardLogger(
        version=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ADAPTER_NAME,
        save_dir=LOG_DIR,
    )
    trainer = Trainer(
        accelerator="gpu",
        devices=1,
        num_nodes=1,
        precision="bf16-mixed",
        accumulate_grad_batches=1,
        max_epochs=-1,
        max_steps=MAX_STEPS,
        log_every_n_steps=1,
        logger=logger,
        enable_checkpointing=False,
        callbacks=[],
        gradient_clip_val=0.5,
        gradient_clip_algorithm="norm",
        reload_dataloaders_every_n_epochs=1,
        val_check_interval=None,
    )
    trainer.fit(model)


if __name__ == "__main__":
    main()
"""


def patch_trainer(trainer_path: Path) -> None:
    text = trainer_path.read_text()
    if "import shutil" not in text:
        if TRAINER_IMPORT_NEEDLE not in text:
            raise RuntimeError("Could not find import block in trainer.py")
        text = text.replace(TRAINER_IMPORT_NEEDLE, TRAINER_IMPORT_NEEDLE + "import shutil\n", 1)

    if "self.save_every_steps" in text and "Saved LoRA-only checkpoint" in text:
        trainer_path.write_text(text)
        return

    start = text.find(TRAINER_BLOCK_START)
    if start == -1:
        raise RuntimeError("Could not find training_step block in trainer.py")
    end = text.find(TRAINER_BLOCK_END, start)
    if end == -1:
        raise RuntimeError("Could not find end of checkpoint block in trainer.py")
    text = text[:start] + TRAINER_REPLACEMENT + text[end:]
    trainer_path.write_text(text)


def write_wrapper(
    wrapper_path: Path,
    dataset_path: str,
    checkpoint_dir: str,
    resume_lora: str,
    adapter_name: str,
    max_steps: int,
    save_every_steps: int,
    keep_last: int,
    log_dir: str,
) -> None:
    wrapper_path.write_text(
        RUN_TRAIN_TEMPLATE.format(
            dataset_path=dataset_path,
            checkpoint_dir=checkpoint_dir,
            resume_lora=resume_lora,
            adapter_name=adapter_name,
            max_steps=max_steps,
            save_every_steps=save_every_steps,
            keep_last=keep_last,
            log_dir=log_dir,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ace-step-dir", required=True)
    parser.add_argument("--dataset-path", required=True)
    parser.add_argument("--checkpoint-dir", required=True)
    parser.add_argument("--resume-lora", default="")
    parser.add_argument("--adapter-name", default="kishore_lora_a100_resume")
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--save-every-steps", type=int, default=100)
    parser.add_argument("--keep-last", type=int, default=2)
    parser.add_argument("--log-dir", default="/runpod-volume/ace_logs")
    args = parser.parse_args()

    ace_step_dir = Path(args.ace_step_dir).resolve()
    trainer_path = ace_step_dir / "trainer.py"
    wrapper_path = ace_step_dir / "run_train_single.py"

    patch_trainer(trainer_path)
    write_wrapper(
        wrapper_path=wrapper_path,
        dataset_path=args.dataset_path,
        checkpoint_dir=args.checkpoint_dir,
        resume_lora=args.resume_lora,
        adapter_name=args.adapter_name,
        max_steps=args.max_steps,
        save_every_steps=args.save_every_steps,
        keep_last=args.keep_last,
        log_dir=args.log_dir,
    )
    print(f"Patched {trainer_path}")
    print(f"Wrote {wrapper_path}")


if __name__ == "__main__":
    main()
