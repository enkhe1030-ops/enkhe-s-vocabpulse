from flask import Flask, Response
import os

app = Flask(__name__)

INDEX_HTML = '''<!DOCTYPE html>
<html lang="mn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VocabPulse - Secure Spaced Repetition App</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Supabase JS SDK (UMD stable version for browser) -->
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#4f46e5">

    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .perspective { perspective: 1000px; }
        .transform-style-3d { transform-style: preserve-3d; }
        .backface-hidden { backface-visibility: hidden; }
        .rotate-y-180 { transform: rotateY(180deg); }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col antialiased select-none">

    <!-- LOGIN / REGISTER MODAL -->
    <div id="authOverlay" class="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-md p-6 sm:p-8 rounded-3xl shadow-2xl border border-slate-100">
            <div class="text-center mb-6">
                <div class="w-12 h-12 bg-indigo-600 text-white rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-lg shadow-indigo-200">
                    <i class="fa-solid fa-shield-halved text-2xl"></i>
                </div>
                <h2 class="text-2xl font-black text-slate-900">VocabPulse</h2>
                <p class="text-xs text-slate-500 mt-1">Supabase Cloud Аюулгүй Систем</p>
            </div>

            <!-- Login Form -->
            <div id="loginForm" class="flex flex-col gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Имэйл хаяг</label>
                    <input type="email" id="loginEmail" autocapitalize="none" autocomplete="off" spellcheck="false" placeholder="жишээ: user@gmail.com" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-indigo-500 font-semibold">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Нууц үг</label>
                    <div class="relative">
                        <input type="password" id="loginPass" placeholder="••••••••" class="w-full border border-slate-200 rounded-xl pl-4 pr-10 py-2.5 text-sm focus:outline-indigo-500">
                        <button type="button" onclick="togglePasswordVisibility('loginPass', 'loginEyeIcon')" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-600">
                            <i id="loginEyeIcon" class="fa-regular fa-eye"></i>
                        </button>
                    </div>
                </div>
                <button onclick="handleLogin()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition mt-2">
                    Нэвтрэх
                </button>
                <div class="text-center text-xs text-slate-500 mt-2">
                    Шинэ хэрэглэгч үү? <button onclick="toggleAuth('register')" class="text-indigo-600 font-bold hover:underline">Бүртгүүлэх</button>
                </div>
            </div>

            <!-- Register Form -->
            <div id="registerForm" class="hidden flex flex-col gap-3">
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 mb-1">Овог *</label>
                        <input type="text" id="regLastName" placeholder="Бат" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-indigo-500 font-semibold">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 mb-1">Нэр *</label>
                        <input type="text" id="regFirstName" placeholder="Болд" class="w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-indigo-500 font-semibold">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Имэйл хаяг *</label>
                    <input type="email" id="regEmail" autocapitalize="none" autocomplete="off" spellcheck="false" placeholder="boldoo@gmail.com" class="w-full border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-indigo-500 font-semibold">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Нууц үг *</label>
                    <div class="relative">
                        <input type="password" id="regPass" placeholder="••••••••" class="w-full border border-slate-200 rounded-xl pl-4 pr-10 py-2.5 text-sm focus:outline-indigo-500">
                        <button type="button" onclick="togglePasswordVisibility('regPass', 'regEyeIcon')" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-indigo-600">
                            <i id="regEyeIcon" class="fa-regular fa-eye"></i>
                        </button>
                    </div>
                </div>
                <button onclick="handleRegister()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition mt-2">
                    Бүртгэл үүсгэх
                </button>
                <div class="text-center text-xs text-slate-500 mt-2">
                    Бүртгэлтэй юу? <button onclick="toggleAuth('login')" class="text-indigo-600 font-bold hover:underline">Нэвтрэх</button>
                </div>
            </div>
        </div>
    </div>

    <!-- EDIT WORD MODAL -->
    <div id="editModal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[90] flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-lg p-6 rounded-3xl shadow-2xl border border-slate-100 flex flex-col gap-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <h3 class="font-extrabold text-lg text-slate-800">Үг Засварлах</h3>
                <button onclick="closeEditModal()" class="text-slate-400 hover:text-slate-600 text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <input type="hidden" id="editWordId">
            <div>
                <label class="block text-xs font-bold text-slate-600 mb-1">Англи үг</label>
                <input type="text" id="editWordText" class="w-full border border-slate-200 rounded-xl px-4 py-2 text-sm font-bold focus:outline-indigo-500">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-600 mb-1">Монгол орчуулга</label>
                <input type="text" id="editTranslationText" class="w-full border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-indigo-500">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-600 mb-1">Түлхүүр санамж (Mnemonic)</label>
                <input type="text" id="editMnemonicText" class="w-full border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-indigo-500">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-600 mb-1">Жишээ өгүүлбэр</label>
                <input type="text" id="editExampleText" class="w-full border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-indigo-500">
            </div>
            <div class="flex justify-end gap-2 mt-2">
                <button onclick="closeEditModal()" class="px-4 py-2 rounded-xl bg-slate-100 font-bold text-xs text-slate-600 hover:bg-slate-200">Цуцлах</button>
                <button onclick="saveEditWord()" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 font-bold text-xs text-white">Хадгалах</button>
            </div>
        </div>
    </div>

    <!-- NIIT YGSIN SAN MODAL -->
    <div id="bankModal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[90] flex items-center justify-center p-4">
        <div class="bg-white w-full max-w-3xl h-[85vh] p-6 rounded-3xl shadow-2xl border border-slate-100 flex flex-col gap-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <div>
                    <h3 class="font-extrabold text-lg text-slate-800">Нийт Үгсийн Сан</h3>
                    <p class="text-xs text-slate-500">CEFR А1-С2 түвшний үгсээс сонгон өөрийн сан руу нэмээрэй</p>
                </div>
                <button onclick="closeBankModal()" class="text-slate-400 hover:text-slate-600 text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div class="flex flex-col sm:flex-row gap-2">
                <input type="text" id="bankSearch" oninput="renderBankWords()" placeholder="Үг эсвэл орчуулгаар хайх..." class="flex-1 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-indigo-500">
                <select id="bankLevelFilter" onchange="renderBankWords()" class="border border-slate-200 rounded-xl px-3 py-2 text-sm font-bold text-slate-600 focus:outline-indigo-500">
                    <option value="ALL">Бүх Түвшин (1,500 үг)</option>
                    <option value="A1">A1 - Анхан шат (250 үг)</option>
                    <option value="A2">A2 - Суурь шат (250 үг)</option>
                    <option value="B1">B1 - Дунд шат (250 үг)</option>
                    <option value="B2">B2 - Ахисан дунд (250 үг)</option>
                    <option value="C1">C1 - Гүнзгий шат (250 үг)</option>
                    <option value="C2">C2 - Дээд шат (250 үг)</option>
                </select>
            </div>

            <div id="bankWordList" class="flex-1 overflow-y-auto flex flex-col divide-y divide-slate-100 border border-slate-200 rounded-2xl pr-1"></div>
        </div>
    </div>

    <!-- Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="bg-indigo-600 text-white p-2.5 rounded-xl shadow-md shadow-indigo-200">
                    <i class="fa-solid font-bold text-xl fa-bolt"></i>
                </div>
                <div>
                    <h1 class="font-extrabold text-xl tracking-tight text-slate-900">VocabPulse</h1>
                    <p class="text-xs text-indigo-600 font-semibold" id="currentUserDisplay">Хэрэглэгч</p>
                </div>
            </div>
            
            <div class="flex items-center gap-3">
                <div class="bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-xl flex items-center gap-2 text-amber-700 text-sm font-bold">
                    <i class="fa-solid fa-fire text-amber-500"></i>
                    <span id="streakCount">1</span> өдөр
                </div>
                <button onclick="handleLogout()" title="Гарах" class="p-2 text-slate-400 hover:text-rose-500 text-lg transition">
                    <i class="fa-solid fa-right-from-bracket"></i>
                </button>
            </div>
        </div>
    </header>

    <!-- EXAM LOCK BANNER -->
    <div id="examLockBanner" class="hidden bg-amber-500 text-white text-xs font-bold px-4 py-3 text-center shadow-inner flex items-center justify-center gap-2">
        <i class="fa-solid fa-lock text-sm"></i>
        <span>Та эхний 30 үгээ цээжилж дуусгасан тул 3 хоног тутамд заавал ШАЛГАЛТ өгөх дүрэм идэвхжлээ! Үргэлжлүүлэн суралцахын тулд шалгалт өгнө үү.</span>
        <button onclick="switchTab('exam')" class="bg-white text-amber-700 px-3 py-1 rounded-lg text-xs font-black shadow hover:bg-slate-100 transition ml-2">Шалгалт өгөх</button>
    </div>

    <!-- Main Content -->
    <main class="flex-1 max-w-4xl w-full mx-auto px-4 py-6 flex flex-col gap-6">

        <!-- Navigation Tabs -->
        <div class="grid grid-cols-5 bg-slate-200/80 p-1.5 rounded-2xl gap-1 text-xs sm:text-sm font-semibold">
            <button onclick="switchTab('flashcards')" id="tab-flashcards" class="tab-btn py-2.5 rounded-xl bg-white text-indigo-600 shadow-sm transition-all flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-layer-group"></i> <span class="hidden sm:inline">Цээжлэх</span>
            </button>
            <button onclick="switchTab('quiz')" id="tab-quiz" class="tab-btn py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition-all flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-circle-question"></i> <span class="hidden sm:inline">Сорилт</span>
            </button>
            <button onclick="switchTab('exam')" id="tab-exam" class="tab-btn py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition-all flex items-center justify-center gap-1.5 relative">
                <i class="fa-solid fa-file-signature"></i> <span class="hidden sm:inline">Шалгалт</span>
                <span id="examDot" class="hidden absolute top-1 right-2 w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
            </button>
            <button onclick="switchTab('wordbook')" id="tab-wordbook" class="tab-btn py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition-all flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-book-bookmark"></i> <span class="hidden sm:inline">Жагсаалт</span>
            </button>
            <button onclick="switchTab('add')" id="tab-add" class="tab-btn py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition-all flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-circle-plus"></i> <span class="hidden sm:inline">Үг нэмэх</span>
            </button>
        </div>

        <!-- 1. Flashcards -->
        <section id="sec-flashcards" class="flex flex-col gap-6">
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-3 w-full sm:w-auto">
                    <div class="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold">
                        <i class="fa-solid fa-brain"></i>
                    </div>
                    <div>
                        <div class="text-xs font-bold uppercase tracking-wider text-slate-400">Марталтын Муруйн Давтамж</div>
                        <div class="text-sm font-bold text-slate-700">Өнөөдөр давтах үгс: <span id="dueWordsCount" class="text-indigo-600 font-black">0</span> / Нийт: <span id="totalWordsCount">0</span></div>
                    </div>
                </div>
                <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                    <button onclick="openBankModal()" class="bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 text-indigo-600 text-xs px-3 py-2 rounded-xl font-bold transition flex items-center gap-1.5">
                        <i class="fa-solid fa-database"></i> Нийт үгсийн сан
                    </button>
                </div>
            </div>

            <div id="cardContainer" class="w-full h-96 perspective cursor-pointer">
                <div id="flashcard" onclick="flipCard()" class="w-full h-full relative transform-style-3d transition-transform duration-500 rounded-3xl shadow-xl bg-white border border-slate-200">
                    <div class="absolute inset-0 backface-hidden p-8 flex flex-col justify-between items-center text-center">
                        <div class="w-full flex justify-between items-center text-slate-400 text-xs font-semibold">
                            <span class="bg-indigo-50 text-indigo-600 px-3 py-1 rounded-full"><i class="fa-solid fa-eye-slash"></i> Active Recall</span>
                            <button onclick="event.stopPropagation(); speakCurrentWord()" class="hover:text-indigo-600 p-2 text-base"><i class="fa-solid fa-volume-high"></i></button>
                        </div>
                        <div>
                            <h2 id="cardWord" class="text-4xl font-black text-slate-800 tracking-tight mb-2">Word</h2>
                            <p id="cardPhonetic" class="text-sm text-indigo-600 font-medium">/wɜːd/</p>
                        </div>
                        <div class="text-xs text-slate-400 font-medium flex items-center gap-1 bg-slate-100 px-4 py-2 rounded-xl">
                            <i class="fa-solid fa-rotate"></i> Таагаад, карт дээр дарж орчуулгыг харна уу
                        </div>
                    </div>

                    <div class="absolute inset-0 backface-hidden rotate-y-180 p-6 flex flex-col justify-between bg-slate-900 text-white rounded-3xl overflow-hidden">
                        <div class="relative z-10 flex justify-between items-center">
                            <span class="bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 px-3 py-1 rounded-full text-xs font-semibold" id="cardIntervalTag">SRS: Day 1</span>
                            <button onclick="event.stopPropagation(); speakCurrentWord()" class="hover:text-indigo-400 p-2 text-base text-slate-300"><i class="fa-solid fa-volume-high"></i></button>
                        </div>

                        <div class="relative z-10 flex flex-col items-center text-center gap-3 my-auto">
                            <img id="cardImage" src="" alt="word image" class="w-24 h-24 object-cover rounded-2xl border-2 border-white/10 shadow-lg">
                            <div>
                                <h3 id="cardTranslation" class="text-3xl font-extrabold text-amber-400 mb-1">Монгол утга</h3>
                                <p id="cardMnemonic" class="text-xs text-slate-300 bg-white/10 p-2.5 rounded-xl border border-white/5 max-w-sm">💡 Түлхүүр холбоос</p>
                            </div>
                        </div>

                        <div class="relative z-10 bg-white/5 p-3 rounded-xl border border-white/10 text-xs text-slate-300 flex items-center justify-between gap-2">
                            <span class="italic text-center flex-1">"<span id="cardExample">Example sentence.</span>"</span>
                            <button onclick="event.stopPropagation(); speakCurrentExample()" title="Өгүүлбэр сонсох" class="text-amber-400 hover:text-amber-300 p-1 text-sm"><i class="fa-solid fa-volume-high"></i></button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex items-center justify-between gap-3">
                <button onclick="srsReview(false)" class="flex-1 py-3.5 rounded-2xl bg-rose-50 hover:bg-rose-100 border border-rose-200 text-rose-600 font-bold transition flex items-center justify-center gap-2">
                    <i class="fa-solid fa-xmark"></i> ❌ Мартагдсан
                </button>
                <button onclick="srsReview(true)" class="flex-1 py-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold shadow-lg shadow-emerald-200 transition flex items-center justify-center gap-2">
                    <i class="fa-solid fa-check"></i> ✅ Цээжилсэн
                </button>
            </div>
        </section>

        <!-- 2. Quiz Section -->
        <section id="sec-quiz" class="hidden flex flex-col gap-6">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div class="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6 pb-4 border-b border-slate-100">
                    <div>
                        <h3 class="font-extrabold text-lg text-slate-800">Үгсийн Сорилт</h3>
                        <p class="text-xs text-slate-500">Зөв хариулсан үгс сорилтоос хасагдана</p>
                    </div>
                    
                    <div class="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-bold gap-1 flex-wrap justify-center">
                        <button onclick="setQuizMode('en-mn')" id="quizModeEnMn" class="px-3 py-1.5 rounded-lg bg-white text-indigo-600 shadow-sm">Англи ➔ Монгол</button>
                        <button onclick="setQuizMode('mn-en')" id="quizModeMnEn" class="px-3 py-1.5 rounded-lg text-slate-500">Монгол ➔ Англи</button>
                        <button onclick="setQuizMode('fill-blank')" id="quizModeFillBlank" class="px-3 py-1.5 rounded-lg text-slate-500">Өгүүлбэр нөхөх</button>
                    </div>
                </div>

                <div id="quizContent" class="flex flex-col gap-6">
                    <div class="bg-indigo-50/70 p-6 rounded-2xl border border-indigo-100 text-center flex flex-col items-center gap-2">
                        <span class="text-xs font-bold text-indigo-500 uppercase tracking-wider" id="quizQuestionType">Асуулт</span>
                        <div class="flex items-center justify-center gap-3">
                            <h2 id="quizQuestion" class="text-2xl sm:text-3xl font-black text-slate-800">Word</h2>
                            <button id="quizQuestionAudio" onclick="speakText(currentQuizQuestionText)" class="text-indigo-600 hover:text-indigo-800 text-xl"><i class="fa-solid fa-volume-high"></i></button>
                        </div>
                    </div>

                    <div id="quizOptions" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>

                    <div id="quizTileContainer" class="hidden flex flex-col gap-4 items-center">
                        <div class="flex items-center gap-2">
                            <span id="constructedWordDisplay" class="text-2xl font-black text-indigo-600 tracking-widest bg-indigo-50 px-6 py-2 rounded-xl border border-indigo-200 min-w-[150px] text-center">--</span>
                            <button onclick="resetTiles()" class="p-2 text-slate-400 hover:text-slate-600 text-sm"><i class="fa-solid fa-arrow-rotate-left"></i> Арилгах</button>
                        </div>
                        <div id="tileButtons" class="flex flex-wrap gap-2 justify-center max-w-sm"></div>
                        <button onclick="checkTileAnswer()" class="w-full max-w-xs py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition mt-2">Шалгах</button>
                        <div id="tileFeedback" class="text-center font-bold text-sm hidden"></div>
                    </div>
                </div>

                <div id="quizCompleted" class="hidden text-center py-10 flex flex-col items-center gap-4">
                    <div class="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center text-2xl font-bold">
                        <i class="fa-solid fa-trophy"></i>
                    </div>
                    <div>
                        <h3 class="text-2xl font-extrabold text-slate-800 mb-1">Баяр хүргэе! 🎉</h3>
                        <p class="text-sm text-slate-500">Та бүх үгээ сайн тааж дуусгалаа!</p>
                    </div>
                    <button onclick="resetQuiz()" class="mt-2 bg-indigo-600 text-white font-bold px-6 py-2.5 rounded-xl hover:bg-indigo-700 transition">Дахин эхлүүлэх</button>
                </div>
            </div>
        </section>

        <!-- 3. Exam Section -->
        <section id="sec-exam" class="hidden flex flex-col gap-6">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div class="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6 pb-4 border-b border-slate-100">
                    <div>
                        <h3 class="font-extrabold text-lg text-slate-800">Иж бүрэн Шалгалт</h3>
                        <p class="text-xs text-slate-500">Эхний 30 үг цээжилсний дараа 3 хоног тутамд заавал өгнө</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <label class="text-xs font-bold text-slate-600">Асуултын тоо:</label>
                        <input type="number" id="examWordCountInput" value="10" min="5" max="100" class="w-16 px-2 py-1.5 border border-slate-200 rounded-xl text-center font-bold text-sm focus:outline-indigo-500">
                        <button onclick="startNewExam()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-xl font-bold transition">Эхлүүлэх</button>
                    </div>
                </div>

                <div id="examActiveBox" class="hidden flex flex-col gap-6">
                    <div class="flex justify-between items-center text-xs font-bold text-slate-400">
                        <span>Асуулт: <span id="examQNum" class="text-indigo-600 font-extrabold">1</span> / <span id="examTotalQ">10</span></span>
                        <span>Оноо: <span id="examScore" class="text-emerald-600 font-extrabold">0</span></span>
                    </div>
                    <div class="bg-slate-50 p-6 rounded-2xl border border-slate-200 text-center">
                        <h3 id="examQuestionText" class="text-2xl font-black text-slate-800">Word</h3>
                    </div>
                    <div id="examOptionsGrid" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
                </div>

                <div id="examHistoryBox" class="flex flex-col gap-4">
                    <h4 class="font-bold text-sm text-slate-700">Шалгалтын түүх & Нийт үнэлгээ</h4>
                    <div id="examHistoryList" class="flex flex-col gap-2"></div>
                </div>
            </div>
        </section>

        <!-- 4. Wordbook -->
        <section id="sec-wordbook" class="hidden flex flex-col gap-4">
            <div class="flex items-center justify-between">
                <h3 class="font-extrabold text-lg text-slate-800">Миний үгсийн сан (<span id="wordCount">0</span>)</h3>
                <button onclick="openBankModal()" class="bg-indigo-50 border border-indigo-200 text-indigo-600 text-xs px-3 py-1.5 rounded-xl font-bold hover:bg-indigo-100 transition">
                    + Нийт үгсийн сангаас авах
                </button>
            </div>
            <div id="wordbookList" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
        </section>

        <!-- 5. Add Word -->
        <section id="sec-add" class="hidden">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm max-w-xl mx-auto flex flex-col gap-4">
                <h3 class="font-extrabold text-lg text-slate-800">Шинэ үг нэмэх</h3>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Англи үг *</label>
                    <div class="flex gap-2">
                        <input type="text" id="newWord" autocapitalize="none" autocomplete="off" spellcheck="false" placeholder="Жишээ: recommend" class="flex-1 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-indigo-500 font-semibold">
                        <button onclick="autoGenerateWordInfo()" id="autoBtn" class="bg-indigo-50 border border-indigo-200 text-indigo-600 text-xs px-3 py-2 rounded-xl font-bold hover:bg-indigo-100 transition flex items-center gap-1">
                            <i class="fa-solid fa-wand-magic-sparkles"></i> Авто засах
                        </button>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Монгол орчуулга *</label>
                    <input type="text" id="newTranslation" placeholder="Жишээ: Санал болгох" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-indigo-500">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Түлхүүр санамж (Mnemonic)</label>
                    <input type="text" id="newMnemonic" placeholder="Заавал бичих шаардлагагүй" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-indigo-500">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Жишээ өгүүлбэр</label>
                    <input type="text" id="newExample" placeholder="Жишээ: I highly recommend this book." class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-indigo-500">
                </div>
                <button onclick="addNewWord()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition shadow-lg shadow-indigo-100 mt-2">
                    <i class="fa-solid fa-plus"></i> Жагсаалтад нэмэх
                </button>
            </div>
        </section>

    </main>

    <script>
        // Supabase Тохиргоо (Өөрийн Supabase Project URL болон Anon Key-г энд оруулна уу)
        const SUPABASE_URL = 'https://aopbyjndymjfkvkbxsui.supabase.co';
        const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFvcGJ5am5keW1qZmt2a2J4c3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI2NzQ5MjcsImV4cCI6MjEwODI1MDkyN30.wvrxumNqdtm4kTKcTp0uP-TdMpZT-mC5j33sCfyqLM0';
        
        let supabaseClient = null;
        try {
            if (window.supabase && typeof window.supabase.createClient === 'function') {
                supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
            }
        } catch (e) {
            console.error("Supabase init error:", e);
        }

        function escapeHTML(str) {
            if (!str) return '';
            return str.replace(/[&<>'"]/g, 
                tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
            );
        }

        const SRS_INTERVALS = [1, 3, 7, 21, 60];

        const core1500Bank = [
            { id: 'a1_1', word: 'apple', level: 'A1', translation: 'Алим', example: 'I eat an apple every day.' },
            { id: 'a1_2', word: 'book', level: 'A1', translation: 'Ном', example: 'She reads a good book.' },
            { id: 'a2_1', word: 'achieve', level: 'A2', translation: 'Хүрэх, биелүүлэх', example: 'You can achieve your dreams.' },
            { id: 'b1_1', word: 'recommend', level: 'B1', translation: 'Санал болгох, зөвлөх', example: 'I highly recommend this movie.' }
        ];

        let currentUserSession = null;
        let userData = { words: [], streak: 1, lastExamDate: Date.now(), examHistory: [] };
        let activeDueWords = [];
        let currentIndex = 0;
        let quizMode = 'en-mn';
        let currentQuizQuestionText = '';
        let currentTargetQuizWord = null;
        let activeQuizWords = [];
        let examQuestions = [];
        let examCurrentIdx = 0;
        let examScoreCount = 0;

        document.addEventListener('DOMContentLoaded', async () => {
            await checkAuth();
        });

        function togglePasswordVisibility(inputId, iconId) {
            const input = document.getElementById(inputId);
            const icon = document.getElementById(iconId);
            if (input.type === 'password') {
                input.type = 'text';
                icon.className = 'fa-regular fa-eye-slash text-indigo-600';
            } else {
                input.type = 'password';
                icon.className = 'fa-regular fa-eye';
            }
        }

        async function checkAuth() {
            if (!supabaseClient) {
                alert("Supabase холболт амжилтгүй боллоо. URL болон Key шалгана уу.");
                return;
            }
            const { data: { session } } = await supabaseClient.auth.getSession();
            if (session) {
                currentUserSession = session.user;
                document.getElementById('authOverlay').classList.add('hidden');
                await loadUserDataFromCloud();
            } else {
                currentUserSession = null;
                document.getElementById('authOverlay').classList.remove('hidden');
            }
        }

        function toggleAuth(type) {
            if (type === 'register') {
                document.getElementById('loginForm').classList.add('hidden');
                document.getElementById('registerForm').classList.remove('hidden');
            } else {
                document.getElementById('registerForm').classList.add('hidden');
                document.getElementById('loginForm').classList.remove('hidden');
            }
        }

        async function handleRegister() {
            const lastName = escapeHTML(document.getElementById('regLastName').value.trim());
            const firstName = escapeHTML(document.getElementById('regFirstName').value.trim());
            const email = document.getElementById('regEmail').value.trim().toLowerCase();
            const password = document.getElementById('regPass').value.trim();

            if (!lastName || !firstName || !email || !password) {
                alert('Бүх талбарыг гүйцэд бөглөнө үү!');
                return;
            }

            const { data, error } = await supabaseClient.auth.signUp({ email, password });
            if (error) {
                alert('Бүртгүүлэхэд алдаа гарлаа: ' + error.message);
                return;
            }

            const userId = data.user.id;
            const defaultWords = [
                { id: 1, word: 'recommend', phonetic: '/ˌrek.əˈmend/', translation: 'Санал болгох, зөвлөх', mnemonic: '', example: 'I highly recommend reading this book.', category: '70% Нийтлэг', srsLevel: 0, nextReviewDate: Date.now(), image: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300' }
            ];

            const initialAppData = {
                words: defaultWords,
                streak: 1,
                lastExamDate: Date.now(),
                examHistory: []
            };

            await supabaseClient.from('user_profiles').insert([
                { id: userId, username: email, first_name: firstName, last_name: lastName, app_data: initialAppData }
            ]);

            alert('Бүртгэл амжилттай үүслээ! Та нэвтэрнэ үү.');
            toggleAuth('login');
        }

        async function handleLogin() {
            const email = document.getElementById('loginEmail').value.trim().toLowerCase();
            const password = document.getElementById('loginPass').value.trim();

            const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
            if (error) {
                alert('Нэвтрэх нэр эсвэл нууц үг буруу байна!');
                return;
            }
            await checkAuth();
        }

        async function handleLogout() {
            await supabaseClient.auth.signOut();
            location.reload();
        }

        async function loadUserDataFromCloud() {
            const { data, error } = await supabaseClient
                .from('user_profiles')
                .select('*')
                .eq('id', currentUserSession.id)
                .single();

            if (data) {
                document.getElementById('currentUserDisplay').innerText = `${data.first_name} (${data.username})`;
                userData = data.app_data || { words: [], streak: 1, lastExamDate: Date.now(), examHistory: [] };
            } else {
                userData = { words: [], streak: 1, lastExamDate: Date.now(), examHistory: [] };
            }

            document.getElementById('streakCount').innerText = userData.streak || 1;
            checkExamRequirement();
            filterSRSWords();
            renderWordbook();
            renderExamHistory();
            initQuiz();
        }

        async function saveUserData() {
            filterSRSWords();
            if (!currentUserSession) return;
            
            await supabaseClient
                .from('user_profiles')
                .update({ app_data: userData, updated_at: new Date() })
                .eq('id', currentUserSession.id);
        }

        function checkExamRequirement() {
            const wordCount = userData.words ? userData.words.length : 0;
            if (wordCount < 30) {
                document.getElementById('examLockBanner').classList.add('hidden');
                document.getElementById('examDot').classList.add('hidden');
                return false;
            }
            const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000;
            const lastExam = userData.lastExamDate || 0;
            const isLocked = (Date.now() - lastExam) > THREE_DAYS_MS;

            if (isLocked) {
                document.getElementById('examLockBanner').classList.remove('hidden');
                document.getElementById('examDot').classList.remove('hidden');
            } else {
                document.getElementById('examLockBanner').classList.add('hidden');
                document.getElementById('examDot').classList.add('hidden');
            }
            return isLocked;
        }

        function filterSRSWords() {
            const now = Date.now();
            activeDueWords = userData.words.filter(w => !w.nextReviewDate || w.nextReviewDate <= now);
            if (activeDueWords.length === 0) activeDueWords = [...userData.words];

            document.getElementById('dueWordsCount').innerText = activeDueWords.length;
            document.getElementById('totalWordsCount').innerText = userData.words.length;
            currentIndex = 0;
            renderFlashcard();
        }

        function srsReview(remembered) {
            if (checkExamRequirement()) {
                alert('Та эхний 30 үгээ цээжилж дуусгасан тул 3 хоног тутамд заавал ШАЛГАЛТ өгөх дүрэм идэвхжлээ!');
                switchTab('exam');
                return;
            }
            if (!activeDueWords || activeDueWords.length === 0) return;
            const w = activeDueWords[currentIndex];

            if (remembered) {
                w.srsLevel = (w.srsLevel || 0) + 1;
                if (w.srsLevel >= SRS_INTERVALS.length) w.srsLevel = SRS_INTERVALS.length - 1;
                w.nextReviewDate = Date.now() + (SRS_INTERVALS[w.srsLevel] * 24 * 60 * 60 * 1000);
            } else {
                w.srsLevel = 0;
                w.nextReviewDate = Date.now();
            }
            saveUserData();
            nextCard();
        }

        function openEditModal(id) {
            const w = userData.words.find(item => item.id === id);
            if (!w) return;
            document.getElementById('editWordId').value = w.id;
            document.getElementById('editWordText').value = w.word;
            document.getElementById('editTranslationText').value = w.translation;
            document.getElementById('editMnemonicText').value = w.mnemonic || '';
            document.getElementById('editExampleText').value = w.example || '';
            document.getElementById('editModal').classList.remove('hidden');
        }

        function closeEditModal() {
            document.getElementById('editModal').classList.add('hidden');
        }

        function saveEditWord() {
            const id = parseInt(document.getElementById('editWordId').value);
            const w = userData.words.find(item => item.id === id);
            if (w) {
                w.word = escapeHTML(document.getElementById('editWordText').value.trim());
                w.translation = escapeHTML(document.getElementById('editTranslationText').value.trim());
                w.mnemonic = escapeHTML(document.getElementById('editMnemonicText').value.trim());
                w.example = escapeHTML(document.getElementById('editExampleText').value.trim());
                saveUserData();
                renderWordbook();
                renderFlashcard();
                closeEditModal();
            }
        }

        function openBankModal() {
            document.getElementById('bankModal').classList.remove('hidden');
            renderBankWords();
        }

        function closeBankModal() {
            document.getElementById('bankModal').classList.add('hidden');
        }

        function renderBankWords() {
            const query = document.getElementById('bankSearch').value.toLowerCase().trim();
            const level = document.getElementById('bankLevelFilter').value;
            const container = document.getElementById('bankWordList');
            container.innerHTML = '';

            const filtered = core1500Bank.filter(b => {
                const matchQ = b.word.toLowerCase().includes(query) || b.translation.toLowerCase().includes(query);
                const matchL = level === 'ALL' || b.level === level;
                return matchQ && matchL;
            });

            filtered.forEach(item => {
                const isAdded = userData.words.some(w => w.word.toLowerCase() === item.word.toLowerCase());
                const div = document.createElement('div');
                div.className = "p-3.5 flex items-center justify-between hover:bg-slate-50 transition border-b border-slate-100 last:border-none";
                div.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div>
                            <div class="font-extrabold text-slate-800 text-sm flex items-center gap-2">
                                ${item.word} <span class="text-[10px] bg-indigo-50 border border-indigo-200 text-indigo-700 px-2 py-0.5 rounded-md font-bold">${item.level}</span>
                            </div>
                            <div class="text-xs text-slate-500 font-medium">${item.translation}</div>
                        </div>
                    </div>
                    ${isAdded ? `<span class="text-emerald-600 font-bold text-xs"><i class="fa-solid fa-check"></i> Нэмэгдсэн</span>` : `<button onclick="addFromBank('${item.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3.5 py-1.5 rounded-xl transition">+ Нэмэх</button>`}
                `;
                container.appendChild(div);
            });
        }

        function addFromBank(bankId) {
            const bItem = core1500Bank.find(b => b.id === bankId);
            if (!bItem) return;
            userData.words.push({
                id: Date.now(),
                word: bItem.word,
                phonetic: `/${bItem.word.toLowerCase()}/`,
                translation: bItem.translation,
                mnemonic: '',
                example: bItem.example,
                category: `CEFR ${bItem.level}`,
                srsLevel: 0,
                nextReviewDate: Date.now(),
                image: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300'
            });
            saveUserData();
            renderBankWords();
            renderWordbook();
        }

        function switchTab(tab) {
            if ((tab === 'flashcards' || tab === 'quiz') && checkExamRequirement()) {
                alert('Та эхний 30 үгээ цээжилж дуусгасан тул 3 хоног тутамд заавал ШАЛГАЛТ өгөх дүрэм идэвхжлээ!');
                tab = 'exam';
            }
            document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('bg-white', 'text-indigo-600', 'shadow-sm');
                b.classList.add('text-slate-600');
            });
            document.getElementById(`sec-${tab}`).classList.remove('hidden');
            const activeBtn = document.getElementById(`tab-${tab}`);
            activeBtn.classList.add('bg-white', 'text-indigo-600', 'shadow-sm');
            activeBtn.classList.remove('text-slate-600');

            if (tab === 'quiz') initQuiz();
            if (tab === 'wordbook') renderWordbook();
            if (tab === 'exam') renderExamHistory();
        }

        function renderFlashcard() {
            if (!activeDueWords || activeDueWords.length === 0) {
                document.getElementById('cardWord').innerText = "Үг байхгүй";
                document.getElementById('cardTranslation').innerText = "Нийт үгсийн сангаас үг нэмнэ үү";
                return;
            }
            const w = activeDueWords[currentIndex];
            document.getElementById('cardWord').innerText = w.word;
            document.getElementById('cardPhonetic').innerText = w.phonetic || '/.../';
            document.getElementById('cardTranslation').innerText = w.translation;
            document.getElementById('cardMnemonic').innerText = '💡 ' + (w.mnemonic || 'Түлхүүр санамж байхгүй');
            document.getElementById('cardExample').innerText = w.example || 'Example sentence.';
            document.getElementById('cardImage').src = w.image || 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300';
            document.getElementById('cardIntervalTag').innerText = `SRS: Day ${SRS_INTERVALS[w.srsLevel || 0]}`;
            document.getElementById('flashcard').classList.remove('rotate-y-180');
        }

        function flipCard() { document.getElementById('flashcard').classList.toggle('rotate-y-180'); }
        function nextCard() {
            if (!activeDueWords || activeDueWords.length === 0) return;
            currentIndex = (currentIndex + 1) % activeDueWords.length;
            renderFlashcard();
        }

        function speakText(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                speechSynthesis.speak(utterance);
            }
        }
        function speakCurrentWord() { if (activeDueWords.length > 0) speakText(activeDueWords[currentIndex].word); }
        function speakCurrentExample() { if (activeDueWords.length > 0) speakText(activeDueWords[currentIndex].example); }

        async function autoGenerateWordInfo() {
            const wordInput = escapeHTML(document.getElementById('newWord').value.trim().toLowerCase());
            if (!wordInput) { alert('Эхлээд англи үгээ оруулна уу!'); return; }
            document.getElementById('newTranslation').value = `${wordInput} орчуулга`;
            document.getElementById('newExample').value = `This is a sentence with ${wordInput}.`;
        }

        function addNewWord() {
            const word = escapeHTML(document.getElementById('newWord').value.trim());
            const translation = escapeHTML(document.getElementById('newTranslation').value.trim());
            const mnemonic = escapeHTML(document.getElementById('newMnemonic').value.trim());
            const example = escapeHTML(document.getElementById('newExample').value.trim());

            if (!word || !translation) { alert('Үг болон орчуулгыг заавал бичнэ үү!'); return; }
            if (userData.words.some(w => w.word.toLowerCase() === word.toLowerCase())) {
                alert('⚠️ Энэ үг аль хэдийнэ нэмэгдсэн байна!');
                return;
            }

            userData.words.push({
                id: Date.now(),
                word: word,
                phonetic: `/${word.toLowerCase()}/`,
                translation: translation,
                mnemonic: mnemonic,
                example: example || `Example sentence for ${word}.`,
                category: 'Хэрэглэгчийн үг',
                srsLevel: 0,
                nextReviewDate: Date.now(),
                image: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300'
            });

            saveUserData();
            document.getElementById('newWord').value = '';
            document.getElementById('newTranslation').value = '';
            document.getElementById('newMnemonic').value = '';
            document.getElementById('newExample').value = '';
            alert('✨ Шинэ үг амжилттай нэмэгдлээ!');
            switchTab('wordbook');
        }

        function setQuizMode(mode) {
            quizMode = mode;
            initQuiz();
        }

        function initQuiz() {
            activeQuizWords = [...userData.words];
            document.getElementById('quizContent').classList.remove('hidden');
            document.getElementById('quizCompleted').classList.add('hidden');
            nextQuizQuestion();
        }

        function resetQuiz() { initQuiz(); }

        function nextQuizQuestion() {
            if (activeQuizWords.length === 0) {
                document.getElementById('quizContent').classList.add('hidden');
                document.getElementById('quizCompleted').classList.remove('hidden');
                return;
            }
            currentTargetQuizWord = activeQuizWords[Math.floor(Math.random() * activeQuizWords.length)];
            const optsContainer = document.getElementById('quizOptions');
            optsContainer.classList.remove('hidden');
            document.getElementById('quizTileContainer').classList.add('hidden');

            let options = [currentTargetQuizWord];
            while (options.length < Math.min(4, userData.words.length)) {
                const rw = userData.words[Math.floor(Math.random() * userData.words.length)];
                if (!options.some(o => o.id === rw.id)) options.push(rw);
            }
            options.sort(() => Math.random() - 0.5);

            document.getElementById('quizQuestion').innerText = currentTargetQuizWord.word;
            optsContainer.innerHTML = '';
            options.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = "p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 font-bold text-slate-700 transition flex items-center justify-between";
                btn.innerHTML = `<span>${opt.translation}</span>`;
                btn.onclick = () => {
                    if (opt.id === currentTargetQuizWord.id) {
                        btn.className = "p-4 rounded-xl border border-emerald-500 bg-emerald-50 text-emerald-700 font-bold flex items-center justify-between";
                        setTimeout(() => {
                            activeQuizWords = activeQuizWords.filter(w => w.id !== currentTargetQuizWord.id);
                            nextQuizQuestion();
                        }, 500);
                    } else {
                        btn.className = "p-4 rounded-xl border border-rose-500 bg-rose-50 text-rose-700 font-bold flex items-center justify-between";
                    }
                };
                optsContainer.appendChild(btn);
            });
        }

        function startNewExam() {
            if (!userData.words || userData.words.length === 0) { alert('Үгсийн сан хоосон байна!'); return; }
            examQuestions = [...userData.words].sort(() => Math.random() - 0.5).slice(0, 10);
            examCurrentIdx = 0;
            examScoreCount = 0;
            document.getElementById('examActiveBox').classList.remove('hidden');
            document.getElementById('examHistoryBox').classList.add('hidden');
            renderExamQuestion();
        }

        function renderExamQuestion() {
            if (examCurrentIdx >= examQuestions.length) {
                finishExam();
                return;
            }
            const q = examQuestions[examCurrentIdx];
            document.getElementById('examQNum').innerText = examCurrentIdx + 1;
            document.getElementById('examQuestionText').innerText = q.word;

            let opts = [q];
            while (opts.length < Math.min(4, userData.words.length)) {
                const rw = userData.words[Math.floor(Math.random() * userData.words.length)];
                if (!opts.some(o => o.id === rw.id)) opts.push(rw);
            }
            opts.sort(() => Math.random() - 0.5);

            const grid = document.getElementById('examOptionsGrid');
            grid.innerHTML = '';
            opts.optsContainer?.innerHTML = '';
            opts.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = "p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 font-bold text-slate-700 transition";
                btn.innerText = opt.translation;
                btn.onclick = () => {
                    if (opt.id === q.id) examScoreCount++;
                    examCurrentIdx++;
                    renderExamQuestion();
                };
                grid.appendChild(btn);
            });
        }

        function finishExam() {
            document.getElementById('examActiveBox').classList.add('hidden');
            document.getElementById('examHistoryBox').classList.remove('hidden');
            const percent = Math.round((examScoreCount / examQuestions.length) * 100);
            
            userData.examHistory.unshift({
                date: new Date().toLocaleString(),
                score: `${examScoreCount}/${examQuestions.length}`,
                percent: `${percent}%`,
                grade: percent >= 90 ? 'A' : percent >= 80 ? 'B' : percent >= 70 ? 'C' : 'D'
            });
            userData.lastExamDate = Date.now();
            saveUserData();
            renderExamHistory();
            alert(`Шалгалт дууслаа! Үнэлгээ: ${percent}%`);
        }

        function renderExamHistory() {
            const container = document.getElementById('examHistoryList');
            container.innerHTML = '';
            if (!userData.examHistory || userData.examHistory.length === 0) {
                container.innerHTML = `<div class="text-xs text-slate-400 italic">Шалгалтын түүх байхгүй байна.</div>`;
                return;
            }
            userData.examHistory.forEach(item => {
                const div = document.createElement('div');
                div.className = "bg-slate-50 p-3 rounded-xl border border-slate-200 flex justify-between items-center text-xs font-semibold";
                div.innerHTML = `<span>${item.date}</span> <span>Оноо: ${item.score} (${item.percent})</span>`;
                container.appendChild(div);
            });
        }

        function renderWordbook() {
            if (!userData.words) return;
            document.getElementById('wordCount').innerText = userData.words.length;
            const container = document.getElementById('wordbookList');
            container.innerHTML = '';
            userData.words.forEach(w => {
                const card = document.createElement('div');
                card.className = "bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between gap-3";
                card.innerHTML = `
                    <div>
                        <h4 class="font-extrabold text-slate-800 text-base">${w.word}</h4>
                        <p class="text-xs text-slate-500 font-medium">${w.translation}</p>
                    </div>
                    <div class="flex items-center gap-1">
                        <button onclick="openEditModal(${w.id})" class="text-slate-400 hover:text-indigo-600 p-2"><i class="fa-solid fa-pen"></i></button>
                        <button onclick="deleteWord(${w.id})" class="text-slate-300 hover:text-rose-500 p-2"><i class="fa-solid fa-trash-can"></i></button>
                    </div>`;
                container.appendChild(card);
            });
        }

        function deleteWord(id) {
            userData.words = userData.words.filter(w => w.id !== id);
            saveUserData();
            renderWordbook();
            renderFlashcard();
        }
    </script>
</body>
</html>'''

@app.get("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html; charset=utf-8")

@app.get("/health")
def health():
    return {"status": "ok", "app": "VocabPulse"}

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
