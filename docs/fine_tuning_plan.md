# Fine-Tuning Plan

This project is not ready to fine-tune yet. The next step is to stabilize the evaluation loop and understand category-level errors.

## Validation Data Rule

`data/gold_validation.json` must remain validation-only. Do not train, tune prompts by memorizing, or fine-tune on this file.

## Future Training Data Sources

- Human-reviewed labels from separate questions.
- Synthetic STEM questions with programmatically verified answers.
- High-confidence pseudo-labels that are reviewed before training.

## Future SFT JSONL Shape

```json
{
  "messages": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "{\"selected_index\": 1}"
    }
  ]
}
```

## Adapter Strategy

Future fine-tuning should use LoRA or QLoRA adapters. Keep training dependencies out of the runtime Docker image.

## Runtime Safety

Do not start fine-tuning automatically. Fine-tuning should be a separate, explicit workflow after the validation loop is stable and after a separate training set exists.

