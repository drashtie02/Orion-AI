# Diagram Export Instructions

This directory contains Mermaid diagram source files (.mmd) for OrionAI architecture documentation.

## Files

- `system_architecture.mmd` - Complete system architecture showing all layers
- `request_flow.mmd` - Step-by-step request processing flow
- `scaling_architecture.mmd` - Kubernetes deployment and autoscaling architecture

## Viewing Diagrams

### GitHub Markdown (Recommended)

Diagrams are embedded in README.md using Mermaid code blocks and render automatically on GitHub.

### Mermaid Live Editor

1. Visit https://mermaid.live/
2. Copy contents of any .mmd file
3. Paste into editor
4. View/export as PNG/SVG

### Mermaid CLI

Install:
```bash
npm install -g @mermaid-js/mermaid-cli
```

Export to PNG:
```bash
mmdc -i diagrams/system_architecture.mmd -o diagrams/system_architecture.png
mmdc -i diagrams/request_flow.mmd -o diagrams/request_flow.png
mmdc -i diagrams/scaling_architecture.mmd -o diagrams/scaling_architecture.png
```

Export to SVG:
```bash
mmdc -i diagrams/system_architecture.mmd -o diagrams/system_architecture.svg
mmdc -i diagrams/request_flow.mmd -o diagrams/request_flow.svg
mmdc -i diagrams/scaling_architecture.mmd -o diagrams/scaling_architecture.svg
```

### VS Code Extension

Install "Markdown Preview Mermaid Support" extension to preview diagrams in VS Code.

## Editing Diagrams

1. Edit .mmd files directly
2. Preview changes using any method above
3. Commit .mmd files to version control
4. Do NOT commit generated PNG/SVG files (they can be regenerated)

## Diagram Syntax

All diagrams use Mermaid syntax:
- https://mermaid.js.org/intro/
- https://mermaid.js.org/syntax/flowchart.html
- https://mermaid.js.org/syntax/graph.html

## Integration

Diagrams are embedded in:
- README.md (main documentation)
- docs/ARCHITECTURE.md (detailed architecture)
