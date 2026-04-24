import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import zhCNCommon from './locales/zh-CN/common.json'
import zhCNAuth from './locales/zh-CN/auth.json'
import zhCNDocuments from './locales/zh-CN/documents.json'
import zhCNChat from './locales/zh-CN/chat.json'
import enCommon from './locales/en/common.json'
import enAuth from './locales/en/auth.json'
import enDocuments from './locales/en/documents.json'
import enChat from './locales/en/chat.json'

const resources = {
  'zh-CN': {
    common: zhCNCommon,
    auth: zhCNAuth,
    documents: zhCNDocuments,
    chat: zhCNChat,
  },
  en: {
    common: enCommon,
    auth: enAuth,
    documents: enDocuments,
    chat: enChat,
  },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'zh-CN',
    debug: false,
    ns: ['common', 'auth', 'documents', 'chat'],
    defaultNS: 'common',
    interpolation: {
      escapeValue: false,
    },
  })

export default i18n
