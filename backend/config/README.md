# Configuration Files

This directory contains JSON configuration files for various Vello modules.

## Files

- `warmup.json` - Warmup Manager configuration (defaults)
- `automation.json` - System automation flags (defaults)

## How It Works

1. **Default values** are stored in JSON files (committed to git)
2. **Secrets and overrides** go in `.env` (NOT committed to git)
3. `.env` values **override** JSON defaults

## Example

### `config/warmup.json` (committed)

```json
{
  "enabled": true,
  "start_volume": 5,
  "max_volume": 50
}
```

### `.env` (not committed)

```bash
# Override specific values
WARMUP_ENABLED=True
WARMUP_START_VOLUME=10
```

The config loader will:

1. Load defaults from `warmup.json`
2. Override with values from `.env` if present
3. Use JSON defaults if `.env` doesn't have the value

## Adding New Config Files

1. Create `config/your_module.json` with defaults
2. Add loading logic in `src/vello/core/config.py`
3. Allow `.env` overrides for sensitive values
