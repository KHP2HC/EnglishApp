import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import { useSettingsStore } from '@/stores/settings.store'

const resources = {
  en: {
    translation: {
      // ── Nav ──
      'nav.home': 'Home',
      'nav.vocab': 'Vocab',
      'nav.grammar': 'Grammar',
      'nav.listening': 'Listening',
      'nav.reading': 'Reading',
      'nav.writing': 'Writing',
      'nav.speaking': 'Speaking',
      'nav.mock': 'Mock',
      'nav.progress': 'Progress',
      'nav.settings': 'Settings',

      // ── Dashboard ──
      'dashboard.greeting.morning': 'Good morning',
      'dashboard.greeting.afternoon': 'Good afternoon',
      'dashboard.greeting.evening': 'Good evening',
      'dashboard.daysToExam': 'days to exam',
      'dashboard.dayStreak': 'day streak',
      'dashboard.dailyGoal': 'Daily Goal',
      'dashboard.wordsLearned': 'Words Learned',
      'dashboard.currentBand': 'Current Band',
      'dashboard.xpThisWeek': 'XP This Week',
      'dashboard.todaysPlan': "Today's Plan",
      'dashboard.wordOfDay': 'Word of the Day',
      'dashboard.noPlan': 'No plan for today yet.',
      'dashboard.generatePlan': 'Generate a study plan →',

      // ── Vocabulary ──
      'vocab.title': 'Vocabulary Practice',
      'vocab.tapToReveal': 'Tap to reveal',
      'vocab.again': 'Again',
      'vocab.hard': 'Hard',
      'vocab.good': 'Good',
      'vocab.easy': 'Easy',
      'vocab.reviewed': 'Cards reviewed',
      'vocab.accuracy': 'Accuracy',
      'vocab.xpEarned': 'XP earned',
      'vocab.nextSession': 'Next session',
      'vocab.tomorrow': 'Tomorrow',
      'vocab.noCards': 'No cards due. Come back tomorrow!',

      // ── Listening ──
      'listening.title': 'Listening Practice',
      'listening.playAudio': 'Play Audio',
      'listening.loading': 'Loading listening tests…',
      'listening.noTests': 'No listening tests available.',
      'listening.results': 'Listening Test Results',
      'listening.estimatedBand': 'Estimated IELTS Band',
      'listening.score': 'Score',

      // ── Speaking ──
      'speaking.title': 'Speaking Practice',
      'speaking.playExaminer': 'Play Examiner (Correct Pronunciation)',
      'speaking.record': 'Record & Evaluate',
      'speaking.listening': 'Listening…',
      'speaking.accuracy': 'Pronunciation Accuracy',
      'speaking.wordsToPractice': 'Words to practice',
      'speaking.startTimer': 'Start Timer',
      'speaking.startPrep': 'Start 1-minute Preparation Timer',

      // ── Writing ──
      'writing.title': 'Writing Practice',
      'writing.taskPrompt': 'Task Prompt',
      'writing.yourEssay': 'Your Essay',
      'writing.getAiFeedback': 'Get AI Feedback',
      'writing.quickLocal': 'Quick Local Analysis (no server needed)',
      'writing.analyzing': 'Analyzing…',
      'writing.wordsMin': 'words minimum',
      'writing.estimatedBand': 'Estimated Band Score',
      'writing.assessmentCriteria': 'Assessment Criteria',

      // ── Progress ──
      'progress.title': 'Your Progress',
      'progress.overview': 'Overview',
      'progress.charts': 'Charts',
      'progress.errorJournal': 'Error Journal',

      // ── Common ──
      'common.loading': 'Loading…',
      'common.next': 'Next',
      'common.back': 'Back',
      'common.save': 'Save',
      'common.cancel': 'Cancel',
      'common.restart': 'Restart',
      'common.level': 'Level',
      'common.xp': 'XP',
    },
  },
  vi: {
    translation: {
      // ── Nav ──
      'nav.home': 'Trang chủ',
      'nav.vocab': 'Từ vựng',
      'nav.grammar': 'Ngữ pháp',
      'nav.listening': 'Nghe',
      'nav.reading': 'Đọc',
      'nav.writing': 'Viết',
      'nav.speaking': 'Nói',
      'nav.mock': 'Thi thử',
      'nav.progress': 'Tiến độ',
      'nav.settings': 'Cài đặt',

      // ── Dashboard ──
      'dashboard.greeting.morning': 'Chào buổi sáng',
      'dashboard.greeting.afternoon': 'Chào buổi chiều',
      'dashboard.greeting.evening': 'Chào buổi tối',
      'dashboard.daysToExam': 'ngày đến kỳ thi',
      'dashboard.dayStreak': 'ngày liên tục',
      'dashboard.dailyGoal': 'Mục tiêu hàng ngày',
      'dashboard.wordsLearned': 'Từ đã học',
      'dashboard.currentBand': 'Band hiện tại',
      'dashboard.xpThisWeek': 'XP tuần này',
      'dashboard.todaysPlan': 'Kế hoạch hôm nay',
      'dashboard.wordOfDay': 'Từ vựng hôm nay',
      'dashboard.noPlan': 'Chưa có kế hoạch cho hôm nay.',
      'dashboard.generatePlan': 'Tạo kế hoạch học tập →',

      // ── Vocabulary ──
      'vocab.title': 'Luyện tập Từ vựng',
      'vocab.tapToReveal': 'Chạm để xem',
      'vocab.again': 'Lại',
      'vocab.hard': 'Khó',
      'vocab.good': 'Tốt',
      'vocab.easy': 'Dễ',
      'vocab.reviewed': 'Thẻ đã ôn',
      'vocab.accuracy': 'Độ chính xác',
      'vocab.xpEarned': 'XP đạt được',
      'vocab.nextSession': 'Buổi học tiếp theo',
      'vocab.tomorrow': 'Ngày mai',
      'vocab.noCards': 'Không có thẻ cần ôn. Hẹn gặp lại ngày mai!',

      // ── Listening ──
      'listening.title': 'Luyện Nghe',
      'listening.playAudio': 'Phát âm thanh',
      'listening.loading': 'Đang tải bài nghe…',
      'listening.noTests': 'Không có bài nghe nào.',
      'listening.results': 'Kết quả bài nghe',
      'listening.estimatedBand': 'Band IELTS ước tính',
      'listening.score': 'Điểm',

      // ── Speaking ──
      'speaking.title': 'Luyện Nói',
      'speaking.playExaminer': 'Phát âm chuẩn (Người khảo)',
      'speaking.record': 'Ghi âm & Đánh giá',
      'speaking.listening': 'Đang nghe…',
      'speaking.accuracy': 'Độ chính xác phát âm',
      'speaking.wordsToPractice': 'Từ cần luyện thêm',
      'speaking.startTimer': 'Bật đồng hồ',
      'speaking.startPrep': 'Bật 1 phút chuẩn bị',

      // ── Writing ──
      'writing.title': 'Luyện Viết',
      'writing.taskPrompt': 'Đề bài',
      'writing.yourEssay': 'Bài viết của bạn',
      'writing.getAiFeedback': 'Nhận phản hồi AI',
      'writing.quickLocal': 'Phân tích nhanh (không cần server)',
      'writing.analyzing': 'Đang phân tích…',
      'writing.wordsMin': 'từ tối thiểu',
      'writing.estimatedBand': 'Band ước tính',
      'writing.assessmentCriteria': 'Tiêu chí đánh giá',

      // ── Progress ──
      'progress.title': 'Tiến độ của bạn',
      'progress.overview': 'Tổng quan',
      'progress.charts': 'Biểu đồ',
      'progress.errorJournal': 'Nhật ký lỗi',

      // ── Common ──
      'common.loading': 'Đang tải…',
      'common.next': 'Tiếp theo',
      'common.back': 'Quay lại',
      'common.save': 'Lưu',
      'common.cancel': 'Hủy',
      'common.restart': 'Làm lại',
      'common.level': 'Cấp độ',
      'common.xp': 'XP',
    },
  },
}

// Initialize with stored language or default to 'en'
const storedLang = (() => {
  try {
    const raw = localStorage.getItem('settings-store')
    if (raw) {
      const parsed = JSON.parse(raw)
      return parsed?.state?.language || 'en'
    }
  } catch { /* ignore */ }
  return 'en'
})()

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: storedLang,
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  })

// Sync i18n language with settings store
useSettingsStore.subscribe((state) => {
  if (state.language && state.language !== i18n.language) {
    i18n.changeLanguage(state.language)
  }
})

export default i18n
