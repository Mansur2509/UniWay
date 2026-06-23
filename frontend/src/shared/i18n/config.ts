export const supportedLocales = ["en", "ru", "uz-Latn", "uz-Cyrl"] as const;

export type LocaleCode = (typeof supportedLocales)[number];

export type LocaleMetadata = {
  code: LocaleCode;
  label: string;
  nativeLabel: string;
  direction: "ltr" | "rtl";
};

export const defaultLocale: LocaleCode = "en";

export const localeMetadata: Record<LocaleCode, LocaleMetadata> = {
  en: {
    code: "en",
    label: "English",
    nativeLabel: "English",
    direction: "ltr"
  },
  ru: {
    code: "ru",
    label: "Russian",
    nativeLabel: "Русский",
    direction: "ltr"
  },
  "uz-Latn": {
    code: "uz-Latn",
    label: "Uzbek (Latin)",
    nativeLabel: "O‘zbekcha",
    direction: "ltr"
  },
  "uz-Cyrl": {
    code: "uz-Cyrl",
    label: "Uzbek (Cyrillic)",
    nativeLabel: "Ўзбекча",
    direction: "ltr"
  }
};

export function isLocaleCode(value: string): value is LocaleCode {
  return supportedLocales.some((locale) => locale === value);
}

