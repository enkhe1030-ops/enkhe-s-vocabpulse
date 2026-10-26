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
    <!-- Supabase JS SDK -->
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    
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

    <!-- EDIT WORD MODAL (Requirement 2: Засах боломж бүх талбарт) -->
    <div id="editModal" style="z-index: 99999; position: fixed; isolation: isolate;" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[99999] flex items-center justify-center p-4">
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
    <div id="bankModal" style="z-index: 9990; position: fixed; isolation: isolate;" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[9990] flex items-center justify-center p-4">
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
                    <option value="ALL">Бүх түвшин</option>
                    <option value="A1">A1 - Анхан шат</option>
                    <option value="A2">A2 - Суурь шат</option>
                    <option value="B1">B1 - Дунд шат</option>
                    <option value="B2">B2 - Ахисан дунд</option>
                    <option value="C1">C1 - Гүнзгий шат</option>
                    <option value="C2">C2 - Дээд шат</option>
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
            </button>
            <button onclick="switchTab('wordbook')" id="tab-wordbook" class="tab-btn py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition-all flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-book-bookmark"></i> <span class="hidden sm:inline">Жагсаалт</span>
            </button>
            <button onclick="switchTab('add')" id="tab-add" class="tab-btn py-2.5 rounded-xl text-slate-600 hover:text-slate-900 transition-all flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-circle-plus"></i> <span class="hidden sm:inline">Үг нэмэх</span>
            </button>
        </div>

        <!-- 1. Flashcards (Цээжлэх хэсэг: Үг / Холбоо үг таб) -->
        <section id="sec-flashcards" class="flex flex-col gap-6">
            <div class="flex items-center justify-center bg-slate-200 p-1 rounded-2xl gap-2 w-fit mx-auto text-xs font-bold">
                <button onclick="setFlashcardMode('word')" id="fcModeWord" class="px-4 py-2 rounded-xl bg-white text-indigo-600 shadow-sm transition">Үг цээжлэх</button>
                <button onclick="setFlashcardMode('phrase')" id="fcModePhrase" class="px-4 py-2 rounded-xl text-slate-600 transition">Холбоо үг цээжлэх</button>
            </div>

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
                            <div class="flex items-center gap-2">
                                <button onclick="event.stopPropagation(); openEditModalFromCard()" class="text-indigo-600 hover:text-indigo-800 p-2 text-sm" title="Картан дээрээс засах"><i class="fa-solid fa-pen"></i></button>
                                <button onclick="event.stopPropagation(); speakCurrentWord()" class="hover:text-indigo-600 p-2 text-base"><i class="fa-solid fa-volume-high"></i></button>
                            </div>
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
                            <div class="flex items-center gap-2">
                                <button onclick="event.stopPropagation(); openEditModalFromCard()" class="text-indigo-300 hover:text-white p-2 text-sm" title="Картан дээрээс засах"><i class="fa-solid fa-pen"></i></button>
                                <button onclick="event.stopPropagation(); speakCurrentWord()" class="hover:text-indigo-400 p-2 text-base text-slate-300"><i class="fa-solid fa-volume-high"></i></button>
                            </div>
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
                <button onclick="previousCard()" class="flex-1 py-3.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition flex items-center justify-center gap-2">
                    <i class="fa-solid fa-chevron-left"></i> Өмнөх
                </button>
                <button onclick="srsReview(true)" class="flex-1 py-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold shadow-lg shadow-emerald-200 transition flex items-center justify-center gap-2">
                    <i class="fa-solid fa-check"></i> Цээжилсэн
                </button>
                <button onclick="nextCard()" class="flex-1 py-3.5 rounded-2xl bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 text-indigo-700 font-bold transition flex items-center justify-center gap-2">
                    Дараах <i class="fa-solid fa-chevron-right"></i>
                </button>
            </div>
        </section>

        <!-- 2. Quiz Section (Сорилт хэсэг: Сонсож олох & Орчуулга хийх таб) -->
        <section id="sec-quiz" class="hidden flex flex-col gap-6">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div class="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6 pb-4 border-b border-slate-100">
                    <div>
                        <h3 class="font-extrabold text-lg text-slate-800">Сорилт & Орчуулга</h3>
                        <p class="text-xs text-slate-500">Үг сорих болон дурын текст/дууны үг орчуулах хэсэг</p>
                    </div>
                    
                    <div class="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-bold gap-1 flex-wrap justify-center">
                        <button onclick="setQuizMode('en-mn')" id="quizModeEnMn" class="px-3 py-1.5 rounded-lg bg-white text-indigo-600 shadow-sm">Англи ➔ Монгол</button>
                        <button onclick="setQuizMode('mn-en')" id="quizModeMnEn" class="px-3 py-1.5 rounded-lg text-slate-500">Монгол ➔ Англи</button>
                        <button onclick="setQuizMode('audio')" id="quizModeAudio" class="px-3 py-1.5 rounded-lg text-slate-500"><i class="fa-solid fa-headphones"></i> Сонсож олох</button>
                        <button onclick="setQuizMode("translate")" id="quizModeTranslate" class="px-3 py-1.5 rounded-lg text-slate-500"><i class="fa-solid fa-language"></i> Орчуулга хийх</button>
                    </div>
                </div>

                <div id="quizContent" class="flex flex-col gap-6">
                    <div id="standardQuizBox" class="flex flex-col gap-6">
                        <div class="bg-indigo-50/70 p-6 rounded-2xl border border-indigo-100 text-center flex flex-col items-center gap-2">
                            <span class="text-xs font-bold text-indigo-500 uppercase tracking-wider" id="quizQuestionType">Асуулт</span>
                            <div class="flex items-center justify-center gap-3">
                                <h2 id="quizQuestion" class="text-2xl sm:text-3xl font-black text-slate-800">Word</h2>
                                <button id="quizQuestionAudio" onclick="speakText(currentQuizQuestionText)" class="text-indigo-600 hover:text-indigo-800 text-xl"><i class="fa-solid fa-volume-high"></i></button>
                            </div>
                        </div>
                        <div id="quizOptions" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
                    </div>

                    <!-- Audio Quiz Box -->
                    <div id="audioQuizBox" class="hidden flex flex-col items-center text-center gap-6 py-8">
                        <div class="w-20 h-20 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-3xl shadow-md animate-pulse">
                            <i class="fa-solid fa-headphones"></i>
                        </div>
                        <div>
                            <h4 class="font-extrabold text-lg text-slate-800 mb-1">Сонсоод зөв хариултыг сонгоно уу</h4>
                            <p class="text-xs text-slate-500">Эхлүүлэх товчийг дарж үгийг сонсоно уу</p>
                        </div>
                        <button onclick="startAudioQuizSession()" class="px-6 py-3 bg-indigo-600 text-white font-bold rounded-xl shadow hover:bg-indigo-700 transition">
                            <i class="fa-solid fa-play"></i> Эхлүүлэх & Үг хэлэх
                        </button>
                        <div id="audioQuizOptions" class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full mt-4 hidden"></div>
                    </div>

                    <!-- Translation Box -->
                    <div id="translationBox" class="hidden flex flex-col gap-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-600 mb-1">Дурын текст эсвэл дууны үг оруулах (Англи ➔ Монгол)</label>
                            <textarea id="translateInputText" rows="5" placeholder="Энд текст эсвэл дууны үгээ хуулж тавина уу..." class="w-full border border-slate-200 rounded-2xl p-4 text-sm focus:outline-indigo-500"></textarea>
                        </div>
                        <button onclick="performTextTranslation()" class="py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition shadow">
                            Орчуулах
                        </button>
                        <div>
                            <label class="block text-xs font-bold text-slate-600 mb-1">Орчуулсан үр дүн</label>
                            <div id="translateResultOutput" class="w-full min-h-[120px] bg-slate-50 border border-slate-200 rounded-2xl p-4 text-sm text-slate-700 whitespace-pre-wrap"></div>
                        </div>
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

        <!-- 3. Exam Section (Шалгалт хэсэг) -->
        <section id="sec-exam" class="hidden flex flex-col gap-6">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div class="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6 pb-4 border-b border-slate-100">
                    <div>
                        <h3 class="font-extrabold text-lg text-slate-800">Иж бүрэн Шалгалт</h3>
                        <p class="text-xs text-slate-500">Тухайн өдрийн болон 7 хоногийн түвшин тус бүрийн шалгалт</p>
                    </div>
                    <div class="flex items-center gap-2 flex-wrap justify-end">
                        <button onclick="startTodayExam()" class="bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 text-indigo-600 text-xs px-3 py-2 rounded-xl font-bold transition">Өнөөдрийн үгсээс шалгах</button>
                        <button onclick="startWeeklyExam()" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-4 py-2 rounded-xl font-bold transition">7 хоногийн шалгалт (Түвшин бүрээс 25)</button>
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

                <div id="examResultDetailBox" class="hidden flex flex-col gap-4">
                    <div class="bg-emerald-50 border border-emerald-200 p-6 rounded-2xl text-center">
                        <h4 class="text-xl font-extrabold text-emerald-800 mb-1" id="examResultTitle">Шалгалт дууслаа!</h4>
                        <p class="text-sm text-emerald-700" id="examResultScoreText">Таны оноо: 10/10</p>
                    </div>
                    <h4 class="font-bold text-sm text-slate-700 mt-2">Алдаа гаргасан үгс (Аль үг дээр алдсаныг харах):</h4>
                    <div id="examMistakesList" class="flex flex-col gap-2"></div>
                    <button onclick="switchTab('exam')" class="mt-2 py-3 bg-indigo-600 text-white font-bold rounded-xl">Буцах</button>
                </div>

                <div id="examHistoryBox" class="flex flex-col gap-4">
                    <h4 class="font-bold text-sm text-slate-700">Шалгалтын түүх & Нийт үнэлгээ</h4>
                    <div id="examHistoryList" class="flex flex-col gap-2"></div>
                </div>
            </div>
        </section>

        <!-- 4. Wordbook (Жагсаалт хэсэг: Миний үгсийн санд зөвхөн цээжилсэн үгс өдөр тус бүрээр табуудад) -->
        <section id="sec-wordbook" class="hidden flex flex-col gap-4">
            <div class="flex items-center justify-between">
                <h3 class="font-extrabold text-lg text-slate-800">Миний үгсийн сан (Цээжилсэн үгс)</h3>
                <button onclick="openBankModal()" class="bg-indigo-50 border border-indigo-200 text-indigo-600 text-xs px-3 py-1.5 rounded-xl font-bold hover:bg-indigo-100 transition">
                    + Нийт үгсийн сангаас авах
                </button>
            </div>
            <!-- Tabs for days -->
            <div id="wordbookDaysTabs" class="flex gap-2 overflow-x-auto pb-2"></div>
            <div id="wordbookList" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
        </section>

        <!-- 5. Add Word (Үг нэмэх хэсэг: Зөвхөн нийт үгсийн санд нэмэгдэнэ) -->
        <section id="sec-add" class="hidden">
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm max-w-xl mx-auto flex flex-col gap-4">
                <h3 class="font-extrabold text-lg text-slate-800">Шинэ үг нэмэх (Нийт үгсийн сан болон бүх хэрэглэгчдэд)</h3>
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Англи үг *</label>
                    <div class="flex gap-2">
                        <input type="text" id="newWord" autocapitalize="none" autocomplete="off" spellcheck="false" placeholder="Жишээ: recommend" class="flex-1 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-indigo-500 font-semibold">
                        <button onclick="autoGenerateWordInfo()" id="autoBtn" class="bg-indigo-50 border border-indigo-200 text-indigo-600 text-xs px-3 py-2 rounded-xl font-bold hover:bg-indigo-100 transition flex items-center gap-1">
                            <i class="fa-solid fa-wand-magic-sparkles"></i> Орчуулга
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
                    <i class="fa-solid fa-plus"></i> Нийт үгсийн санд нэмэх
                </button>
            </div>
        </section>

    </main>

    <script>
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

        const SRS_INTERVALS = [1/24, 1, 3, 7, 14, 30, 60];

        const levelWordLists = {
          "A1": ["a", "an", "the", "I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their", "this", "that", "these", "those", "who", "what", "where", "when", "why", "how", "yes", "no", "not", "all", "some", "any", "many", "much", "more", "most", "less", "few", "one", "two", "three", "first", "last", "new", "old", "good", "bad", "big", "small", "long", "short", "high", "low", "hot", "cold", "happy", "sad", "easy", "hard", "right", "wrong", "same", "different", "important", "possible", "able", "can", "could", "will", "would", "should", "must", "may", "go", "come", "get", "make", "do", "have", "be", "say", "see", "know", "think", "want", "need", "like", "love", "work", "play", "eat", "drink", "sleep", "read", "write"],
          "A2": ["about", "above", "across", "after", "against", "along", "among", "around", "before", "behind", "below", "beside", "between", "beyond", "during", "inside", "outside", "near", "next", "onto", "over", "past", "through", "toward", "under", "until", "within", "without", "according", "actually", "advice", "affect", "afford", "agree", "allow", "although", "amount", "appear", "apply", "area", "arrive", "article", "attention", "avoid", "aware", "basic", "believe", "belong", "benefit", "bill", "borrow", "break", "business", "cancel", "career", "cause", "center", "certain", "change", "choice", "choose", "common", "compare", "complete", "condition", "consider", "continue", "control", "correct", "cost", "create", "culture", "customer", "daily", "decide", "decision", "deliver", "depend", "describe", "design", "develop", "die", "difference", "difficult", "direction", "discover", "discuss", "disease", "distance", "divide", "education", "effect", "effort", "either", "else", "empty", "energy", "enjoy", "enough", "enter"],
          "B1": ["abandon", "ability", "abroad", "absence", "absorb", "abstract", "academic", "accept", "access", "accompany", "accomplish", "account", "accurate", "achieve", "acknowledge", "acquire", "adapt", "additional", "adequate", "adjust", "administration", "admire", "admit", "adopt", "advance", "advantage", "adventure", "advertise", "advocate", "alternative", "ambition", "analyze", "announce", "annual", "anticipate", "anxiety", "apologize", "apparent", "appeal", "appreciate", "approach", "appropriate", "approve", "argue", "arrangement", "assess", "assignment", "assist", "assume", "atmosphere", "attach", "attempt", "attitude", "attract", "authority", "available", "average", "avoid", "background", "balance", "barrier", "basis", "behavior", "belief", "blame", "board", "boundary", "branch", "budget", "candidate", "capable", "capacity", "capture", "category", "challenge", "circumstance", "claim", "clarify", "classic", "client", "climate", "colleague", "combine", "comfort", "command", "commit", "communicate", "community", "company", "complex", "concentrate", "concept", "concern", "conclude", "conduct", "confidence", "conflict", "confuse", "connect", "consequence"],
          "B2": ["abolish", "abrupt", "absence", "absolute", "abstract", "accelerate", "accessible", "accommodate", "accumulate", "accusation", "adjacent", "advocate", "aesthetic", "albeit", "allocate", "alter", "ambiguous", "amend", "analogy", "anticipate", "arbitrary", "articulate", "aspire", "assert", "assess", "asset", "assign", "assumption", "assurance", "attain", "attribute", "authentic", "autonomous", "avenue", "bias", "coincide", "collaborate", "commence", "commission", "commodity", "compatible", "compensate", "compile", "complement", "comply", "component", "comprehensive", "comprise", "compromise", "conceive", "concurrent", "confer", "confine", "conform", "consensus", "consent", "consecutive", "constrain", "consult", "contemplate", "contradict", "controversial", "convene", "convey", "conviction", "coordinate", "corporate", "correspond", "criterion", "crucial", "cumulative", "curriculum", "cynical", "decade", "decisive", "dedicated", "deficiency", "depict", "deploy", "derive", "deteriorate", "devise", "dilemma", "diminish", "discrete", "displace", "dispose", "distinct", "distort", "diverse", "doctrine", "domestic", "dominant", "duration", "elaborate", "eligible", "eliminate", "elite", "embody", "empirical"],
          "C1": ["aberration", "abhor", "abject", "abrogate", "abscond", "abstruse", "accolade", "accretion", "acumen", "adamant", "admonish", "adulterate", "aesthetic", "affinity", "alleviate", "aloof", "altruistic", "ambiguity", "ameliorate", "amenable", "anachronism", "analogous", "anomaly", "antagonize", "antipathy", "apathy", "appease", "apprehensive", "arbitrary", "ardent", "arduous", "articulate", "ascertain", "ascetic", "assiduous", "astute", "audacious", "augment", "austere", "autonomy", "aversion", "belittle", "benevolent", "benign", "bolster", "brevity", "cajole", "candid", "capricious", "catalyst", "caustic", "censure", "cerebral", "charisma", "circumvent", "clandestine", "coalesce", "coercion", "cogent", "coherent", "complacent", "concise", "concede", "condescending", "condone", "conducive", "conjecture", "connoisseur", "consensus", "contentious", "contrite", "convoluted", "copious", "corroborate", "credence", "cryptic", "culpable", "cursory", "cynical", "dearth", "debacle", "decorum", "deference", "delineate", "demur", "denounce", "deride", "desolate", "despondent", "deterrent", "detriment", "deviate", "dexterous", "dichotomy", "diffident", "digression", "diligent", "discern", "disparate", "disseminate"],
          "C2": ["abstruse", "accede", "acrimony", "adumbrate", "alacrity", "anathema", "apocryphal", "approbation", "assiduity", "assuage", "attenuate", "avarice", "bellicose", "bombastic", "cacophony", "calumny", "capitulate", "castigate", "chicanery", "churlish", "circumlocution", "cogitation", "commensurate", "compunction", "confluence", "connivance", "consummate", "contumacious", "contravene", "convivial", "credulous", "cupidity", "debilitate", "decorous", "deleterious", "demagogue", "denouement", "desultory", "diatribe", "didactic", "diffidence", "dilatory", "disingenuous", "dissonance", "ebullient", "effervescent", "egregious", "elicit", "emollient", "encomium", "endemic", "enervate", "ephemeral", "epiphany", "equivocation", "erudition", "exacerbate", "excoriate", "exigency", "expatiate", "expeditious", "extol", "fallacious", "fastidious", "fecund", "felicitous", "fervid", "flagrant", "florid", "foment", "fortuitous", "fractious", "fulminate", "garrulous", "grandiloquent", "gratuitous", "harangue", "hegemony", "iconoclast", "immutable", "impecunious", "impertinent", "impetuous", "inchoate", "incipient", "inculcate", "indefatigable", "ineffable", "inexorable", "ingenuous", "inimical", "inscrutable", "insipid", "insolent", "intrepid", "invective", "invidious", "irascible", "laconic", "largesse"]
        };
        
        const samplePhrases = [
            { id: 'p1', word: 'take off', translation: 'онгоц хөөрөх, тайлах', example: 'The plane will take off soon.' },
            { id: 'p2', word: 'give up', translation: 'бууж өгөх', example: 'Never give up on your dreams.' },
            { id: 'p3', word: 'look forward to', translation: 'тэсэн ядан хүлээх', example: 'I look forward to seeing you.' },
            { id: 'p4', word: 'turn down', translation: 'чангыг багасгах, татгалзах', example: 'Please turn down the music.' }
        ];

        function makeBankExample(word, level) {
            return `I encountered the word "${word}" in our English study session.`;
        }

        let globalWordBank = Object.entries(levelWordLists).flatMap(([level, words]) =>
            words.map((word, i) => ({
                id: `${level.toLowerCase()}_${i+1}`, word, level,
                translation: ({apple:'Алим', book:'Ном', achieve:'Хүрэх', recommend:'Санал болгох'})[word.toLowerCase()] || '',
                mnemonic: '', example: makeBankExample(word, level)
            }))
        );

        let currentUserSession = null;
        let userData = { words: [], phrases: [], streak: 1, lastExamDate: Date.now(), examHistory: [] };
        let activeDueWords = [];
        let currentIndex = 0;
        let flashcardMode = 'word';
        let quizMode = 'en-mn';
        let currentQuizQuestionText = '';
        let currentTargetQuizWord = null;
        let activeQuizWords = [];
        let examQuestions = [];
        let examCurrentIdx = 0;
        let examScoreCount = 0;
        let examCurrentMistakes = [];

        document.addEventListener('DOMContentLoaded', async () => {
            await syncGlobalBankFromCloud();
            await checkAuth();
        });

        async function syncGlobalBankFromCloud() {
            if (!supabaseClient) return;
            try {
                const { data } = await supabaseClient.from('global_word_bank').select('*');
                if (data && data.length > 0) {
                    const existingMap = new Map(globalWordBank.map(w => [w.word.toLowerCase(), w]));
                    data.forEach(item => {
                        if (existingMap.has(item.word.toLowerCase())) {
                            Object.assign(existingMap.get(item.word.toLowerCase()), item);
                        } else {
                            globalWordBank.push(item);
                        }
                    });
                }
            } catch (e) { console.error("Global bank sync error:", e); }
        }

        async function saveWordToGlobalCloud(wordObj) {
            if (!supabaseClient) return;
            try {
                await supabaseClient.from('global_word_bank').upsert([wordObj], { onConflict: 'word' });
            } catch (e) { console.error("Save global bank error:", e); }
        }

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
            if (!supabaseClient) return;
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
            const initialAppData = {
                words: [],
                phrases: samplePhrases,
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
                userData = data.app_data || { words: [], phrases: samplePhrases, streak: 1, lastExamDate: Date.now(), examHistory: [] };
                if (!userData.phrases) userData.phrases = samplePhrases;
            } else {
                userData = { words: [], phrases: samplePhrases, streak: 1, lastExamDate: Date.now(), examHistory: [] };
            }

            document.getElementById('streakCount').innerText = userData.streak || 1;
            filterSRSWords();
            renderWordbookDaysTabs();
            renderExamHistory();
            initQuiz();
        }

        async function saveUserData() {
            if (!currentUserSession) return;
            await supabaseClient
                .from('user_profiles')
                .update({ app_data: userData, updated_at: new Date() })
                .eq('id', currentUserSession.id);
        }

        function filterSRSWords() {
            const now = Date.now();
            const sourceList = flashcardMode === 'word' ? (userData.words || []) : (userData.phrases || []);
            activeDueWords = sourceList.filter(w => !w.nextReviewDate || w.nextReviewDate <= now);
            document.getElementById('dueWordsCount').innerText = activeDueWords.length;
            document.getElementById('totalWordsCount').innerText = sourceList.length;
            currentIndex = 0;
            renderFlashcard();
        }

        function setFlashcardMode(mode) {
            flashcardMode = mode;
            document.getElementById('fcModeWord').className = mode === 'word' ? 'px-4 py-2 rounded-xl bg-white text-indigo-600 shadow-sm transition' : 'px-4 py-2 rounded-xl text-slate-600 transition';
            document.getElementById('fcModePhrase').className = mode === 'phrase' ? 'px-4 py-2 rounded-xl bg-white text-indigo-600 shadow-sm transition' : 'px-4 py-2 rounded-xl text-slate-600 transition';
            filterSRSWords();
        }

        function srsReview(remembered) {
            if (!activeDueWords || activeDueWords.length === 0) return;
            const w = activeDueWords[currentIndex];
            if (remembered) {
                w.srsLevel = Math.min((w.srsLevel || 0) + 1, SRS_INTERVALS.length - 1);
                w.lastReviewedAt = Date.now();
                w.nextReviewDate = Date.now() + (SRS_INTERVALS[w.srsLevel] * 24 * 60 * 60 * 1000);
                w.learnedDate = w.learnedDate || new Date().toISOString().slice(0, 10);
            } else {
                w.srsLevel = 0;
                w.nextReviewDate = Date.now() + 10 * 60 * 1000;
            }
            saveUserData();
            filterSRSWords();
            renderWordbookDaysTabs();
        }

        // Requirement 2: Бүх талбарт засах боломжтой байх
        function openEditModal(id, isPhrase = false) {
            const list = isPhrase ? userData.phrases : userData.words;
            const w = list.find(item => String(item.id) === String(id));
            if (!w) return;
            document.getElementById('editWordId').value = w.id;
            document.getElementById('editWordText').value = w.word;
            document.getElementById('editTranslationText').value = w.translation;
            document.getElementById('editMnemonicText').value = w.mnemonic || '';
            document.getElementById('editExampleText').value = w.example || '';
            document.getElementById('editModal').classList.remove('hidden');
        }

        function openEditModalFromCard() {
            if (!activeDueWords || activeDueWords.length === 0) return;
            const w = activeDueWords[currentIndex];
            openEditModal(w.id, flashcardMode === 'phrase');
        }

        function closeEditModal() {
            document.getElementById('editModal').classList.add('hidden');
        }

        function saveEditWord() {
            const id = document.getElementById('editWordId').value;
            const newWordText = document.getElementById('editWordText').value.trim();
            const newTransText = document.getElementById('editTranslationText').value.trim();
            const newMnemText = document.getElementById('editMnemonicText').value.trim();
            const newExText = document.getElementById('editExampleText').value.trim();

            // Бүх талбарт (Миний үгсийн сан, Нийт үгсийн сан, Картууд) шинэчлэгдэх ёстой
            [userData.words, userData.phrases, globalWordBank].forEach(collection => {
                if (!collection) return;
                collection.forEach(item => {
                    if (String(item.id) === String(id) || item.word.toLowerCase() === newWordText.toLowerCase()) {
                        item.word = newWordText;
                        item.translation = newTransText;
                        item.mnemonic = newMnemText;
                        item.example = newExText;
                    }
                });
            });

            saveUserData();
            filterSRSWords();
            renderWordbookDaysTabs();
            renderBankWords();
            closeEditModal();
            alert('Амжилттай засагдлаа!');
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

            const filtered = globalWordBank.filter(b => {
                const matchQ = b.word.toLowerCase().includes(query) || (b.translation && b.translation.toLowerCase().includes(query));
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
                                ${escapeHTML(item.word)} <span class="text-[10px] bg-indigo-50 border border-indigo-200 text-indigo-700 px-2 py-0.5 rounded-md font-bold">${item.level || 'A1'}</span>
                            </div>
                            <div class="text-xs text-slate-500 font-medium">${escapeHTML(item.translation || 'Орчуулгагүй')}</div>
                        </div>
                    </div>
                    <div class="flex gap-2 items-center">
                        ${isAdded ? `<span class="text-emerald-600 font-bold text-xs">Нэмэгдсэн</span>` : `<button onclick="addFromBank('${item.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3 py-1.5 rounded-xl">+ Миний санд авах</button>`}
                        <button onclick="openEditModal('${item.id}')" class="text-indigo-600 text-xs font-bold px-2 py-1 rounded-lg border">Засах</button>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        async function addFromBank(bankId) {
            await syncGlobalBankFromCloud();
            const bItem = globalWordBank.find(b => String(b.id) === String(bankId));
            if (!bItem) return;
            if (userData.words.some(w => w.word.toLowerCase() === bItem.word.toLowerCase())) {
                alert('Энэ үг таны санд аль хэдийн байна.');
                return;
            }
            userData.words.push({
                id: Date.now() + Math.random(),
                word: bItem.word,
                phonetic: `/${bItem.word.toLowerCase()}/`,
                translation: bItem.translation || "Орчуулга байхгүй",
                mnemonic: bItem.mnemonic || '',
                example: bItem.example || '',
                category: `CEFR ${bItem.level || 'A1'}`,
                srsLevel: 0,
                nextReviewDate: Date.now(),
                learnedDate: new Date().toISOString().slice(0, 10),
                image: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300'
            });
            await saveUserData();
            renderBankWords();
            renderWordbookDaysTabs();
            filterSRSWords();
            alert('Амжилттай миний үгсийн санд нэмэгдлээ.');
        }

        function switchTab(tab) {
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
            if (tab === 'wordbook') renderWordbookDaysTabs();
            if (tab === 'exam') renderExamHistory();
        }

        function renderFlashcard() {
            if (!activeDueWords || activeDueWords.length === 0) {
                document.getElementById('cardWord').innerText = "Давтах үг алга";
                document.getElementById('cardTranslation').innerText = "Өнөөдрийн давтах үгс дууссан байна.";
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
            currentIndex = Math.min(currentIndex + 1, activeDueWords.length - 1);
            renderFlashcard();
        }
        function previousCard() {
            if (!activeDueWords || activeDueWords.length === 0) return;
            currentIndex = Math.max(0, currentIndex - 1);
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

        async function fetchTranslationApi(word) {
            try {
                const response = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(word)}&langpair=en|mn`);
                const data = await response.json();
                return data?.responseData?.translatedText || '';
            } catch (_) { return ''; }
        }

        async function autoGenerateWordInfo() {
            const word = document.getElementById('newWord').value.trim().toLowerCase();
            if (!word) { alert('Эхлээд англи үгээ оруулна уу!'); return; }
            const btn = document.getElementById('autoBtn');
            btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Орчуулж байна...';
            try {
                const translation = await fetchTranslationApi(word);
                document.getElementById('newTranslation').value = translation || '';
                document.getElementById('newExample').value = `I like to learn about "${word}".`;
            } catch (_) {
                alert('Орчуулга татаж чадсангүй.');
            } finally {
                btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Орчуулга';
            }
        }

        // Requirement 3 & 5: Шинэ үг нэмэхэд зөвхөн нийт үгсийн санд нэмэгдэж, бүх хэрэглэгчдэд харагдана
        async function addNewWord() {
            const word = escapeHTML(document.getElementById('newWord').value.trim());
            const translation = escapeHTML(document.getElementById('newTranslation').value.trim());
            const mnemonic = escapeHTML(document.getElementById('newMnemonic').value.trim());
            const example = escapeHTML(document.getElementById('newExample').value.trim());

            if (!word || !translation) { alert('Үг болон орчуулгыг заавал бичнэ үү!'); return; }
            
            const newBankItem = {
                id: `custom_${Date.now()}`,
                word,
                translation,
                mnemonic,
                example: example || `Example sentence for ${word}.`,
                level: 'A1'
            };

            globalWordBank.unshift(newBankItem);
            await saveWordToGlobalCloud(newBankItem);

            ['newWord','newTranslation','newMnemonic','newExample'].forEach(id => document.getElementById(id).value = '');
            alert('✨ Шинэ үг нийт үгсийн санд болон бүх хэрэглэгчдэд амжилттай нэмэгдлээ!');
            openBankModal();
        }

        function setQuizMode(mode) {
            quizMode = mode;
            ['en-mn','mn-en','audio','translate'].forEach(m => {
                const btnId = m === 'en-mn' ? 'quizModeEnMn' : (m === 'mn-en' ? 'quizModeMnEn' : (m === 'audio' ? 'quizModeAudio' : 'quizModeTranslate'));
                const btn = document.getElementById(btnId);
                if (!btn) return;
                btn.className = m === mode ? 'px-3 py-1.5 rounded-lg bg-white text-indigo-600 shadow-sm' : 'px-3 py-1.5 rounded-lg text-slate-500';
            });
            initQuiz();
        }

        function initQuiz() {
            activeQuizWords = [...(userData.words || [])];
            document.getElementById('quizContent').classList.remove('hidden');
            document.getElementById('quizCompleted').classList.add('hidden');
            
            document.getElementById('standardQuizBox').classList.add('hidden');
            document.getElementById('audioQuizBox').classList.add('hidden');
            document.getElementById('translationBox').classList.add('hidden');

            if (quizMode === 'audio') {
                document.getElementById('audioQuizBox').classList.remove('hidden');
            } else if (quizMode === 'translate') {
                document.getElementById('translationBox').classList.remove('hidden');
            } else {
                document.getElementById('standardQuizBox').classList.remove('hidden');
                nextQuizQuestion();
            }
        }

        function resetQuiz() { initQuiz(); }

        function nextQuizQuestion() {
            if (activeQuizWords.length === 0) {
                document.getElementById('standardQuizBox').classList.add('hidden');
                document.getElementById('quizCompleted').classList.remove('hidden');
                return;
            }
            currentTargetQuizWord = activeQuizWords[Math.floor(Math.random() * activeQuizWords.length)];
            const optsContainer = document.getElementById('quizOptions');

            let options = [currentTargetQuizWord];
            while (options.length < Math.min(4, userData.words.length)) {
                const rw = userData.words[Math.floor(Math.random() * userData.words.length)];
                if (!options.some(o => o.id === rw.id)) options.push(rw);
            }
            options.sort(() => Math.random() - 0.5);

            document.getElementById('quizQuestionType').innerText = quizMode === 'en-mn' ? 'Англи ➔ Монгол' : 'Монгол ➔ Англи';
            document.getElementById('quizQuestion').innerText = quizMode === 'en-mn' ? currentTargetQuizWord.word : currentTargetQuizWord.translation;
            currentQuizQuestionText = currentTargetQuizWord.word;

            optsContainer.innerHTML = '';
            options.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = "p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 font-bold text-slate-700 transition flex items-center justify-between";
                btn.innerHTML = `<span>${quizMode === 'en-mn' ? opt.translation : opt.word}</span>`;
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

        // Сорилт: Англи үгийг сонсоод зөв хариултыг сонгох (Автоматаар хэлнэ)
        function startAudioQuizSession() {
            if (!userData.words || userData.words.length === 0) {
                alert('Таны үгсийн сан хоосон байна.');
                return;
            }
            currentTargetQuizWord = userData.words[Math.floor(Math.random() * userData.words.length)];
            speakText(currentTargetQuizWord.word);

            let options = [currentTargetQuizWord];
            while (options.length < Math.min(4, userData.words.length)) {
                const rw = userData.words[Math.floor(Math.random() * userData.words.length)];
                if (!options.some(o => o.id === rw.id)) options.push(rw);
            }
            options.sort(() => Math.random() - 0.5);

            const optGrid = document.getElementById('audioQuizOptions');
            optGrid.classList.remove('hidden');
            optGrid.innerHTML = '';
            options.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = "p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 font-bold text-slate-700 transition";
                btn.innerText = opt.translation;
                btn.onclick = () => {
                    if (opt.id === currentTargetQuizWord.id) {
                        alert('Зөв хариуллаа! 🎉');
                        startAudioQuizSession();
                    } else {
                        alert('Буруу байна, дахин сонсоно уу.');
                        speakText(currentTargetQuizWord.word);
                    }
                };
                optGrid.appendChild(btn);
            });
        }

        // Сорилт: Орчуулга хийх хэсэг (Дурын текст, дууны үг орчуулах)
        async function performTextTranslation() {
            const txt = document.getElementById('translateInputText').value.trim();
            if (!txt) { alert('Орчуулах текстээ оруулна уу.'); return; }
            const out = document.getElementById('translateResultOutput');
            out.innerText = 'Орчуулж байна...';
            try {
                const res = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(txt)}&langpair=en|mn`);
                const data = await res.json();
                out.innerText = data?.responseData?.translatedText || 'Орчуулга гарсангүй.';
            } catch (_) {
                out.innerText = 'Орчуулга хийхэд алдаа гарлаа.';
            }
        }

        // Шалгалт: Тухайн өдөрт үзсэн бүх үгээс шалгалт авах
        function startTodayExam() {
            const today = new Date().toISOString().slice(0, 10);
            const todaysWords = (userData.words || []).filter(w => w.learnedDate === today);
            if (todaysWords.length === 0) {
                alert('Өнөөдөр цээжилсэн үг байхгүй байна. Бүх үгсээс шалгалт авъя.');
                startCustomExam(userData.words);
                return;
            }
            startCustomExam(todaysWords);
        }

        // Шалгалт: 7 хоногт үзсэн бүх үгээс, түвшин бүрээс 25 үгээр шалгалт авах
        function startWeeklyExam() {
            let pool = [];
            ['A1','A2','B1','B2','C1','C2'].forEach(lvl => {
                const lvlWords = (userData.words || []).filter(w => w.category && w.category.includes(lvl));
                const shuffled = [...lvlWords].sort(() => Math.random() - 0.5).slice(0, 25);
                pool.push(...shuffled);
            });
            if (pool.length === 0) pool = [...(userData.words || [])];
            if (pool.length === 0) { alert('Үгсийн сан хоосон байна!'); return; }
            startCustomExam(pool.slice(0, 100));
        }

        function startCustomExam(wordList) {
            if (!wordList || wordList.length === 0) { alert('Шалгалт авах үг олдсонгүй!'); return; }
            examQuestions = [...wordList].sort(() => Math.random() - 0.5);
            examCurrentIdx = 0;
            examScoreCount = 0;
            examCurrentMistakes = [];
            document.getElementById('examActiveBox').classList.remove('hidden');
            document.getElementById('examHistoryBox').classList.add('hidden');
            document.getElementById('examResultDetailBox').classList.add('hidden');
            renderExamQuestion();
        }

        function renderExamQuestion() {
            if (examCurrentIdx >= examQuestions.length) {
                finishExam();
                return;
            }
            const q = examQuestions[examCurrentIdx];
            document.getElementById('examQNum').innerText = examCurrentIdx + 1;
            document.getElementById('examTotalQ').innerText = examQuestions.length;
            document.getElementById('examScore').innerText = examScoreCount;
            document.getElementById('examQuestionText').innerText = q.word;

            let opts = [q];
            while (opts.length < Math.min(4, userData.words.length)) {
                const rw = userData.words[Math.floor(Math.random() * userData.words.length)];
                if (!opts.some(o => o.id === rw.id)) opts.push(rw);
            }
            opts.sort(() => Math.random() - 0.5);

            const grid = document.getElementById('examOptionsGrid');
            grid.innerHTML = '';
            opts.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = "p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-indigo-50 font-bold text-slate-700 transition";
                btn.innerText = opt.translation;
                btn.onclick = () => {
                    if (opt.id === q.id) {
                        examScoreCount++;
                    } else {
                        // Аль үг дээр алдсаныг бүртгэх
                        examCurrentMistakes.push({ word: q.word, correctTranslation: q.translation, selectedTranslation: opt.translation });
                    }
                    examCurrentIdx++;
                    renderExamQuestion();
                };
                grid.appendChild(btn);
            });
        }

        function finishExam() {
            document.getElementById('examActiveBox').classList.add('hidden');
            document.getElementById('examResultDetailBox').classList.remove('hidden');
            const percent = Math.round((examScoreCount / examQuestions.length) * 100);
            
            document.getElementById('examResultTitle').innerText = `Шалгалт дууслаа! Үнэлгээ: ${percent}%`;
            document.getElementById('examResultScoreText').innerText = `Оноо: ${examScoreCount} / ${examQuestions.length}`;

            const mistakesContainer = document.getElementById('examMistakesList');
            mistakesContainer.innerHTML = '';
            if (examCurrentMistakes.length === 0) {
                mistakesContainer.innerHTML = `<div class="text-xs text-emerald-600 font-bold">Баяр хүргэе! Та ямар ч алдаа гаргасангүй.</div>`;
            } else {
                examCurrentMistakes.forEach(m => {
                    const div = document.createElement('div');
                    div.className = "bg-rose-50 border border-rose-200 p-3 rounded-xl text-xs flex justify-between items-center text-slate-700 font-semibold";
                    div.innerHTML = `<span>Англи үг: <b>${m.word}</b></span> <span>Зөв утга: ${m.correctTranslation}</span>`;
                    mistakesContainer.appendChild(div);
                });
            }

            userData.examHistory.unshift({
                date: new Date().toLocaleString(),
                score: `${examScoreCount}/${examQuestions.length}`,
                percent: `${percent}%`
            });
            saveUserData();
            renderExamHistory();
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

        // Requirement 4: Жагсаалт хэсгийн Миний үгсийн санд зөвхөн цээжилсэн үгсийг өдөр тус бүрээр таб хэлбэрээр харуулах
        function renderWordbookDaysTabs() {
            const learnedWords = (userData.words || []).filter(w => (w.srsLevel || 0) > 0 && w.learnedDate);
            document.getElementById('wordCount') && (document.getElementById('wordCount').innerText = learnedWords.length);
            
            const daysMap = {};
            learnedWords.forEach(w => {
                daysMap[w.learnedDate] = daysMap[w.learnedDate] || [];
                daysMap[w.learnedDate].push(w);
            });

            const dates = Object.keys(daysMap).sort().reverse();
            const tabsContainer = document.getElementById('wordbookDaysTabs');
            tabsContainer.innerHTML = '';

            if (dates.length === 0) {
                document.getElementById('wordbookList').innerHTML = `<div class="col-span-2 text-center text-xs text-slate-400 italic py-6">Цээжилсэн үг одоогоор байхгүй байна. Картаас "Цээжилсэн" товч дарж цээжлээрэй.</div>`;
                return;
            }

            dates.forEach((dateStr, idx) => {
                const btn = document.createElement('button');
                btn.className = `px-4 py-2 rounded-xl text-xs font-bold transition ${idx === 0 ? 'bg-indigo-600 text-white shadow' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`;
                btn.innerText = `${dateStr} (${daysMap[dateStr].length} үг)`;
                btn.onclick = () => {
                    document.querySelectorAll('#wordbookDaysTabs button').forEach(b => b.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition');
                    btn.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white shadow transition';
                    renderWordbookCards(daysMap[dateStr]);
                };
                tabsContainer.appendChild(btn);
            });

            renderWordbookCards(daysMap[dates[0]]);
        }

        function renderWordbookCards(wordsArr) {
            const container = document.getElementById('wordbookList');
            container.innerHTML = '';
            wordsArr.forEach(w => {
                const card = document.createElement('div');
                card.className = "bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between gap-3";
                card.innerHTML = `
                    <div>
                        <h4 class="font-extrabold text-slate-800 text-base">${escapeHTML(w.word)} <span class="text-[10px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-md">Цээжилсэн</span></h4>
                        <p class="text-xs text-slate-500 font-medium">${escapeHTML(w.translation || '')}</p>
                        ${w.example ? `<p class="text-xs text-slate-500 mt-1 italic">"${escapeHTML(w.example)}"</p>` : ''}
                    </div>
                    <div class="flex items-center gap-1">
                        <button onclick="openEditModal(${w.id})" class="text-slate-400 hover:text-indigo-600 p-2" title="Засах"><i class="fa-solid fa-pen"></i></button>
                        <button onclick="deleteWord(${w.id})" class="text-slate-300 hover:text-rose-500 p-2" title="Устгах"><i class="fa-solid fa-trash-can"></i></button>
                    </div>`;
                container.appendChild(card);
            });
        }

        function deleteWord(id) {
            userData.words = userData.words.filter(w => String(w.id) !== String(id));
            saveUserData();
            renderWordbookDaysTabs();
            filterSRSWords();
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
