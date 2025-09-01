

# Zippy – AI-Powered Figma-to-Code Generator

> An AI-driven tool that converts **Figma designs → export-ready code**.  
> Built as my **capstone project at Western Sydney University** in collaboration with ThinkGrid.

---

## About
Zippy automates the **design-to-code process** that is normally slow, inconsistent, and error-prone.  
Using **Python, Figma API, and GPT-4 Vision**, it generates HTML/CSS scaffolding with ~80% accuracy — cutting conversion time by 70%.

👉 For full technical breakdown, see the [PRD.md](./PRD.md).  
Please install the following libraries to run the application:
pip install flask
pip install flask-socketio
pip install requests
pip install werkzeug
pip install Pillow
pip install torch torchvision
pip install openai
pip install transformers
pip install certifi


---

## Features
- ✅ Input **Figma URLs** & validate links  
- ✅ Extract frames & group **screen variations**  
- ✅ AI-powered analysis (ResNet + GPT-4 Vision)  
- ✅ Generate **HTML/CSS scaffolding**  
- ✅ Interactive UI: preview, select, export screens  
- ✅ Error handling with clear UX  

---

## Tech Stack
- **Frontend:** HTML, CSS (Bootstrap, custom), JS (DataTables)  
- **Backend:** Python (Flask, Torch, Transformers, Pillow)  
- **AI Models:** ResNet50, GPT-4 Vision (OpenAI API)  
- **Design API:** Figma REST API  

---

## Impact
- **70% faster** design-to-code workflow  
- **80% automation** of code scaffolding  
- Cleaner, reusable HTML/CSS exports  

---

## My Role
- Built responsive **frontend UI/UX**  
- Integrated **Figma API validation & error handling**  
- Developed AI clustering pipeline (`analyze.py`)  
- Authored documentation (Proposal, PRD, SAD)  

---

## Demo
1. Enter Figma URL → Validate  
2. Extract frames → Preview variations  
3. Export → HTML/CSS scaffolding  

---

## 🚀 Roadmap
- [ ] Add React/Next.js code generation  
- [ ] CI/CD deployment pipeline  
- [ ] Fine-tuned AI model for higher accuracy  
- [ ] VS Code plugin for workflow integration  

---

## 📂 Repo Structure
├── analyze.py # AI clustering + embeddings
├── displayJS.js # Frontend display logic
├── displaycss.css # UI styles
├── errorPageJS.js # Error handling
├── errorPagecss.css # Error page styles
├── index.css # Landing page styles
├── PRD.md # Full Product Requirements Document
├── docs/ # University reports
│ ├── PX_ProjectProposal.pdf
│ ├── SAD_Report_Final_PX.pdf
│ └── PX_PA2409.pdf
