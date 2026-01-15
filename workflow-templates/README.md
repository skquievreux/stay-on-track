# GitHub Actions Workflow Templates

This directory contains workflow templates ready to be deployed to an organization-level `.github` repository.

## 📁 Structure

```
workflow-templates/
├── ci.yml                          # CI Pipeline workflow
├── ci.properties.json              # Metadata for GitHub UI
├── release.yml                     # Semantic Release workflow
├── release.properties.json
├── dashboard-sync.yml              # Dashboard synchronization
├── dashboard-sync.properties.json
├── ecosystem-guard.yml             # Security & dependency monitoring
├── ecosystem-guard.properties.json
├── rollout-standards.yml           # Deployment governance
└── rollout-standards.properties.json
```

## 🚀 Deployment

### Automated Setup

Use the provided script to automatically create/update your organization's `.github` repository:

```bash
# Install dependencies if needed
npm install

# Run the setup script
npx tsx scripts/setup-organization-workflows.ts --org <your-organization-name>

# Dry run to preview changes
npx tsx scripts/setup-organization-workflows.ts --org <your-organization-name> --dry-run
```

### Manual Setup

1. **Create Organization Repository**
   ```bash
   gh repo create <org>/.github --public
   ```

2. **Clone the Repository**
   ```bash
   gh repo clone <org>/.github
   cd .github
   ```

3. **Copy Templates**
   ```bash
   mkdir -p workflow-templates
   cp /path/to/this/directory/* workflow-templates/
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add workflow templates"
   git push
   ```

## 📋 Template Metadata

Each `.yml` workflow has a corresponding `.properties.json` file that defines:

- **name**: Display name in GitHub UI
- **description**: What the workflow does
- **iconName**: Icon from [Octicons](https://primer.style/octicons/)
- **categories**: Array of categories (e.g., "CI", "Deployment")
- **filePatterns**: File patterns that suggest this workflow

Example:
```json
{
  "name": "CI Pipeline",
  "description": "Continuous Integration with linting and building",
  "iconName": "check-circle",
  "categories": ["Continuous Integration"],
  "filePatterns": ["package.json", "*.ts", "*.js"]
}
```

## 🔧 Customization

### Adding a New Template

1. Create the workflow file: `my-workflow.yml`
2. Create metadata file: `my-workflow.properties.json`
3. Run the setup script to deploy

### Updating Existing Templates

1. Edit the `.yml` file in this directory
2. Run the setup script to sync changes
3. Existing repositories must manually update their workflows

## 📚 Available Workflows

### 🔄 CI Pipeline
- **Triggers**: Push to main/master, Pull Requests
- **Actions**: Lint → Build → Verify
- **Required**: `npm run lint`, `npm run build`, `npm run verify`

### 📦 Semantic Release
- **Triggers**: Push to main/master
- **Actions**: Analyze commits → Generate version → Create release
- **Required Secrets**: `GH_TOKEN`

### 🔄 Dashboard Sync
- **Triggers**: Schedule (daily), Manual
- **Actions**: Sync documentation and metrics
- **Required**: Project-specific configuration

### 🛡️ Ecosystem Guard
- **Triggers**: Schedule (weekly), Pull Requests
- **Actions**: Dependency audit → Security scan → Health check
- **Required**: None

### 🚀 Rollout Standards
- **Triggers**: Manual, Release creation
- **Actions**: Quality gates → Deployment validation
- **Required**: Deployment-specific secrets

## 🔗 References

- [GitHub: Creating Workflow Templates](https://docs.github.com/en/actions/using-workflows/creating-starter-workflows-for-your-organization)
- [ADR-011: Organization-Wide Workflow Templates](../docs/adr/011-organization-workflow-templates.md)
- [Octicons Icon Reference](https://primer.style/octicons/)

## 📞 Support

For issues or questions:
1. Check the [ADR documentation](../docs/adr/011-organization-workflow-templates.md)
2. Review GitHub's [official documentation](https://docs.github.com/en/actions)
3. Open an issue in this repository

---

**Last Updated**: 2025-12-17  
**Maintained by**: DevOps Team
