# 📑 Product Requirements Document (PRD) – Zippy

**Project Type:** University Capstone (Western Sydney University – PA2409, 2024)  
**Client:** ThinkGrid (Director of Technology, Beno Mathew)  
**Team Size:** 5  
**Role (Hana Pham):** Frontend + AI Integration + Documentation Lead  
**Tech Stack:** Python, JavaScript, OpenAI API (GPT-4 Vision), Figma API, ResNet50, Transformers, Bootstrap, DataTables, CSS/JS  

---

## 1. Problem Statement
Design-to-code conversion is a major bottleneck in software development.  
- Designers spend hours manually converting Figma screens into code.  
- Developers produce inconsistent results, leading to errors and delays.  
- Existing plugins (e.g., Builder.io, Clapy, TeleportHQ) only convert **components**, not full screens:contentReference[oaicite:0]{index=0}.  

This creates **higher costs, longer delivery times, and reduced quality** for businesses.  

---

## 2. Solution
**Zippy** is an **AI-powered code generation tool** that automates ~80% of the design-to-code workflow.  

### Core Features
1. **Figma URL Input & Validation** – detects invalid links and prompts fixes:contentReference[oaicite:1]{index=1}.  
2. **Frame Extraction** – retrieves all screens & variations via Figma API:contentReference[oaicite:2]{index=2}.  
3. **AI-Powered Analysis** – combines ResNet50 embeddings + GPT-4 Vision to cluster similar screens:contentReference[oaicite:3]{index=3}.  
4. **Code Generation** – outputs HTML/CSS scaffolding for front-end use (future: React).  
5. **Interactive UI** – preview, select, and export screens in a clean interface:contentReference[oaicite:4]{index=4}.  
6. **Error Handling** – custom error pages with clear UX feedback:contentReference[oaicite:5]{index=5}.  

---

## 3. Goals & Success Metrics
- Reduce design-to-code conversion time by **≥70%**.  
- Automate at least **80%** of code scaffolding.  
- Provide **preview & export workflows** for usability.  
- Deliver **clean, maintainable code** for dev integration.  

---

## 4. System Overview
**Workflow:**  
1. User enters a **Figma URL**.  
2. Zippy validates → extracts frames using **Figma API**.  
3. Frames analyzed with **ResNet50 + GPT-4 Vision** for clustering.  
4. Screens displayed in an **interactive table** (DataTables.js).  
5. User selects → exports code as **HTML/CSS**.  

**Constraints:**  
- Works with **Figma templates only**.  
- Dependent on **Figma API & OpenAI API availability**.  
- Processing time increases with number of screens:contentReference[oaicite:6]{index=6}.  

---

## 5. My Contributions (Hana Pham)
- Designed and implemented **responsive frontend UI** (CSS/Bootstrap).  
- Built **Figma API integration** + error handling workflows.  
- Developed **Python AI pipeline** (`analyze.py`) for screen clustering.  
- Authored major documentation (Proposal, Project Plan, SAD Report).  

---

## 6. Risks & Mitigations
- **API downtime (Figma/OpenAI)** → fallback error notices + retry logic:contentReference[oaicite:7]{index=7}.  
- **High cost of GPT-4** → explore Gemini or fine-tuned open-source models:contentReference[oaicite:8]{index=8}.  
- **Team inexperience with new tools** → dedicated learning sprints + knowledge sharing.  

---

## 7. Future Roadmap
- [ ] Extend exports to **React/Next.js components**.  
- [ ] Add **CI/CD pipeline** for deployment.  
- [ ] Fine-tune AI model for higher accuracy.  
- [ ] Build VS Code plugin for **designer → developer integration**.  

---

## 8. Documentation & References
- [📘 Project Proposal (PX_ProjectProposal.pdf)](./docs/PX_ProjectProposal.pdf)  
- [📘 Project Plan (PX_PA2409.pdf)](./docs/PX_PA2409.pdf)  
- [📘 System Analysis & Design Report (SAD_Report_Final_PX.pdf)](./docs/SAD_Report_Final_PX.pdf)  

---

## 9. Impact
Zippy demonstrates how **AI + developer tooling** can transform workflows:  
- Reduced time-to-market.  
- Lowered development costs.  
- Enabled designers to integrate directly with engineers.  

This project proves the feasibility of **AI-powered design-to-code automation** and sets the stage for scaling to production-grade developer tools.  
