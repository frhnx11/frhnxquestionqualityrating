# Release Instructions for UPSC Question Analyzer

## How to Create a New Release

### 1. Update Version
Edit `version.txt` with the new version number (e.g., `1.0.1`)

### 2. Commit Changes
```bash
git add .
git commit -m "Release v1.0.1"
git push origin main
```

### 3. Create and Push a Version Tag
```bash
git tag v1.0.1
git push origin v1.0.1
```

### 4. GitHub Actions Will Automatically:
- Build executables for Windows, macOS, and Linux
- Create a GitHub release
- Upload all executables to the release

### 5. Update Download Page
Edit `docs/index.html` and update the GitHub username:
```javascript
const GITHUB_REPO = 'YOUR_USERNAME/upsc-question-analyzer';
```

### 6. Enable GitHub Pages
1. Go to your repository Settings
2. Navigate to Pages
3. Source: Deploy from a branch
4. Branch: main, folder: /docs
5. Save

Your download page will be available at:
`https://YOUR_USERNAME.github.io/upsc-question-analyzer/`

## Manual Build Instructions

If you want to build locally:

### Windows
```bash
python build_windows.py
```

### macOS
```bash
python build_mac.py
```

### Linux
```bash
python build_linux.py
```

## Testing Before Release
1. Run the app locally: `python app.py`
2. Verify Ollama connection works
3. Test question analysis
4. Check Excel export

## Release Checklist
- [ ] Version updated in version.txt
- [ ] All features tested
- [ ] README updated if needed
- [ ] GitHub username updated in docs/index.html
- [ ] Previous releases tested for upgrade path

## Troubleshooting

### GitHub Actions Failing
- Check requirements.txt is complete
- Ensure all imports are handled in the spec file
- Review build logs for missing dependencies

### PyInstaller Issues
- Add missing modules to hiddenimports in spec file
- Include data files in datas list
- Test on target platform before release