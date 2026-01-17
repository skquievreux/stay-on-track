# Troubleshooting Guide

## Common Issues

### Application Won't Start

**Symptoms:**
- Double-clicking the executable does nothing
- No system tray icon appears
- Application crashes immediately

**Solutions:**

1. **Check if already running**
   ```
   - Look for the 📊 icon in system tray
   - Open Task Manager (Ctrl+Shift+Esc)
   - Look for "StayOnTrack.exe" process
   - If found, end the process and try again
   ```

2. **Run as Administrator**
   ```
   - Right-click StayOnTrack.exe
   - Select "Run as administrator"
   ```

3. **Check Windows Defender**
   ```
   - Windows may block unsigned executables
   - Add exception in Windows Security
   - Settings → Update & Security → Windows Security → Virus & threat protection
   - Manage settings → Add exclusion → Folder
   - Select Stay-On-Track installation folder
   ```

4. **Reinstall**
   ```
   - Uninstall via Control Panel
   - Download latest installer from GitHub Releases
   - Run installer as administrator
   ```

### Reminders Not Appearing

**Symptoms:**
- No popup dialogs at 15-minute intervals
- No sound notifications

**Solutions:**

1. **Check time window**
   ```
   - Right-click tray icon → Settings
   - Verify Start Time and End Time
   - Ensure current time is within this window
   ```

2. **Check system time**
   ```
   - Reminders align to :00, :15, :30, :45
   - If system time is incorrect, reminders won't trigger
   - Sync system time: Settings → Time & Language → Date & time
   ```

3. **Restart application**
   ```
   - Right-click tray icon → Exit
   - Start Stay-On-Track again
   ```

### Data Not Saving

**Symptoms:**
- CSV files are empty
- No logs in Documents folder
- History window shows no entries

**Solutions:**

1. **Check data folder**
   ```
   - Open: C:\Users\YourName\Documents\StayOnTrack
   - Verify folder exists and is writable
   - Check for logs_YYYY-MM-DD.csv files
   ```

2. **Check permissions**
   ```
   - Right-click StayOnTrack folder
   - Properties → Security
   - Ensure your user has "Write" permissions
   ```

3. **Check disk space**
   ```
   - Ensure C: drive has free space
   - CSV files are small, but folder must be writable
   ```

4. **Reset configuration**
   ```
   - Close Stay-On-Track
   - Delete: C:\Users\YourName\Documents\StayOnTrack\config.json
   - Restart Stay-On-Track
   - Reconfigure settings
   ```

### Analytics Not Working

**Symptoms:**
- Analytics window is empty
- Categories show 0%
- No daily breakdown

**Solutions:**

1. **Check data availability**
   ```
   - Analytics requires at least 1 day of data
   - Verify CSV files exist in data folder
   - Check that CSV files contain entries
   ```

2. **Check date range**
   ```
   - Select "Last 7 days" or "Last 30 days"
   - Ensure you have data within that range
   ```

3. **Rebuild learned keywords**
   ```
   - Close Stay-On-Track
   - Delete: C:\Users\YourName\Documents\StayOnTrack\learned_keywords.json
   - Restart Stay-On-Track
   - File will be recreated with defaults
   ```

### Auto-Start Not Working

**Symptoms:**
- Application doesn't start with Windows
- Must manually launch after boot

**Solutions:**

1. **Check startup settings**
   ```
   - Open Task Manager (Ctrl+Shift+Esc)
   - Go to "Startup" tab
   - Find "Stay On Track"
   - Ensure Status is "Enabled"
   ```

2. **Re-enable via installer**
   ```
   - Run installer again
   - Select "Automatically start Stay On Track when Windows starts"
   - Complete installation
   ```

3. **Manual registry entry**
   ```
   - Press Win+R
   - Type: shell:startup
   - Create shortcut to StayOnTrack.exe in this folder
   ```

## Error Messages

### "Failed to load configuration"

**Cause:** Corrupted `config.json` file

**Solution:**
```
1. Close Stay-On-Track
2. Delete: C:\Users\YourName\Documents\StayOnTrack\config.json
3. Restart Stay-On-Track
4. Reconfigure settings
```

### "Unable to write to CSV file"

**Cause:** Insufficient permissions or disk full

**Solution:**
```
1. Check disk space on C: drive
2. Verify folder permissions (see "Data Not Saving" above)
3. Try running as administrator
```

### "Python DLL not found"

**Cause:** Missing runtime dependencies (rare with installer)

**Solution:**
```
1. Download and install Visual C++ Redistributable:
   https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Restart computer
3. Try running Stay-On-Track again
```

## Performance Issues

### High CPU Usage

**Symptoms:**
- StayOnTrack.exe using >5% CPU constantly

**Solutions:**
```
1. Restart application
2. Check for multiple instances in Task Manager
3. Reinstall from latest release
```

### High Memory Usage

**Symptoms:**
- StayOnTrack.exe using >100MB RAM

**Solutions:**
```
1. Normal usage: 30-50MB
2. If higher, restart application
3. Check for memory leaks (report as bug)
```

## Data Recovery

### Recovering Lost Data

**If CSV files are deleted:**
```
1. Check Recycle Bin
2. Use file recovery software (e.g., Recuva)
3. Restore from backup (if available)
```

**If CSV files are corrupted:**
```
1. Open file in text editor
2. Check for malformed lines
3. Manually fix or remove corrupted lines
4. Save and reload in Stay-On-Track
```

## Reporting Bugs

If you encounter an issue not listed here:

1. **Gather information:**
   - Windows version
   - Stay-On-Track version
   - Steps to reproduce
   - Error messages (if any)
   - Screenshots

2. **Check existing issues:**
   - https://github.com/skquievreux/stay-on-track/issues

3. **Create new issue:**
   - Use bug report template
   - Include all gathered information
   - Be as specific as possible

## Getting Help

**Documentation:**
- [User Guide](../02-implementation/user-guide.md)
- [Analytics Guide](../02-implementation/analytics.md)
- [Best Practices](../02-implementation/BEST_PRACTICES.md)

**Community:**
- GitHub Discussions: https://github.com/skquievreux/stay-on-track/discussions
- GitHub Issues: https://github.com/skquievreux/stay-on-track/issues

---

**Last Updated:** 2026-01-17  
**Version:** 1.3.x
