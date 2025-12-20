<div align="center">

# 🩺 Mocha - Pediatric Virtual Patient Training

<img width="800" alt="Mocha Banner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />

**An AI-powered virtual patient training platform for medical students to practice pediatric clinical examination skills**

[![React](https://img.shields.io/badge/React-19.2-blue?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.2-purple?logo=vite)](https://vitejs.dev/)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-2.5_Flash-orange?logo=google)](https://ai.google.dev/)

[Demo](#demo) • [Features](#features) • [Getting Started](#getting-started) • [Usage](#usage) • [Tech Stack](#tech-stack)

</div>

---

## 📖 Overview

**Mocha** (Vietnamese: Medical Online Consultation Helper Application) is an interactive virtual patient training platform designed for medical students and healthcare professionals to practice pediatric clinical examination skills. The application simulates realistic patient consultations using Google's Gemini AI, allowing users to:

- Practice history-taking and physical examination
- Develop diagnostic reasoning skills
- Receive AI-powered feedback on clinical performance

## ✨ Features

### 🎯 Virtual Patient Simulation
- **Realistic patient encounters**: AI-powered virtual patients respond naturally to clinical questions
- **Multiple clinical systems**: Respiratory, cardiovascular, gastrointestinal, neurological, infectious, endocrine, renal, and hematological cases
- **Age-appropriate scenarios**: From neonates to adolescents (0-18 years)
- **Difficulty levels**: Easy, medium, and hard cases with varying complexity

### 📝 Clinical Training
- **History taking**: Practice comprehensive patient interviews
- **Physical examination simulation**: Request and interpret examination findings
- **Diagnosis submission**: Document provisional and differential diagnoses
- **Management planning**: Develop treatment and follow-up plans

### ⭐ AI-Powered Evaluation
- **Detailed scoring**: Assessment across 4 domains (history, physical exam, diagnosis, management)
- **Strengths & weaknesses**: Personalized feedback on performance
- **Improvement suggestions**: Actionable recommendations for skill development
- **Score visualization**: Clear progress tracking with visual indicators

### 💾 Session Management
- **Persistent sessions**: All training sessions saved locally
- **Session history**: Review past cases and evaluations
- **Progress tracking**: Monitor improvement over time

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.0 or higher
- **npm** or **yarn** package manager
- **Google Gemini API key** ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/biomed-assistant.git
   cd biomed-assistant
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   
   Copy the example environment file and add your Gemini API key:
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local`:
   ```env
   VITE_GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm run preview
```

## 📱 Usage

### Starting a Training Session

1. **Click "Bắt đầu ca mới"** (Start new case) on the home screen
2. **Choose case type**:
   - **Ca ngẫu nhiên** (Random case): System generates a random patient
   - **Ca tùy chỉnh** (Custom case): Select clinical system, age group, and difficulty
3. **Begin consultation**: The virtual patient will present their chief complaint

### Conducting the Consultation

- Ask questions as you would with a real patient
- Request physical examination findings
- Gather sufficient information before making a diagnosis
- Minimum 5 question-answer exchanges recommended

### Submitting Diagnosis

1. Click **"Tiến hành chẩn đoán"** (Proceed to diagnosis)
2. Enter:
   - **Chẩn đoán sơ bộ** (Provisional diagnosis) - Required
   - **Chẩn đoán phân biệt** (Differential diagnoses) - Optional
   - **Kế hoạch xử trí** (Management plan) - Required
3. Submit for AI evaluation

### Reviewing Results

- View overall score and sub-scores
- Read detailed feedback on strengths and weaknesses
- Review improvement suggestions
- Access session history from the sidebar

## 🛠 Tech Stack

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling (via CDN)
- **react-markdown** - Markdown rendering

### AI/Backend
- **Google Gemini 2.5 Flash** - AI model for conversation & evaluation
- **Local Storage** - Session persistence

### Development
- **ESLint** - Code linting
- **Prettier** - Code formatting

## 📁 Project Structure

```
biomed-assistant/
├── components/           # React components
│   ├── CaseTypeModal.tsx    # Case selection modal
│   ├── DiagnosisForm.tsx    # Diagnosis submission form
│   ├── FeedbackPanel.tsx    # Evaluation results display
│   ├── Icons.tsx            # SVG icon components
│   ├── InputArea.tsx        # Chat input component
│   ├── MessageBubble.tsx    # Chat message display
│   └── Sidebar.tsx          # Navigation sidebar
├── services/
│   └── geminiService.ts     # Gemini AI integration
├── App.tsx                  # Main application component
├── constants.ts             # App constants & AI prompts
├── types.ts                 # TypeScript type definitions
├── index.tsx                # Application entry point
├── index.html               # HTML template
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies & scripts
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_GEMINI_API_KEY` | Google Gemini API key | Yes |

### Customization

- **AI Prompts**: Edit `constants.ts` to modify AI behavior
- **Clinical Systems**: Add/modify systems in `constants.ts`
- **Scoring Criteria**: Adjust evaluation prompts in `constants.ts`

## 🇻🇳 Language

The application is currently in **Vietnamese** as it's designed for Vietnamese medical students. The interface includes:
- Vietnamese clinical terminology
- Vietnamese patient names
- Vietnamese UI labels

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for powering the virtual patient interactions
- [Tailwind CSS](https://tailwindcss.com/) for the styling framework
- Medical professionals who provided clinical expertise

---

<div align="center">

**Made with ❤️ for medical education**

</div>
