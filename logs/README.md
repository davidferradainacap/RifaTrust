# Logs Directory

This directory stores application logs for monitoring and debugging.

## Log Files

- `django.log` - General application errors and warnings
- `security.log` - Security-related events (failed logins, permission denials, etc.)

## Configuration

Logs are configured in `config/settings.py`:
- Maximum size: 15MB per file
- Backup count: 10 files
- Rotation: Automatic when size limit is reached

## Security Note

⚠️ **Never commit log files to version control**  
Log files may contain sensitive information and should be kept private.

This directory should exist but remain empty in the repository.
