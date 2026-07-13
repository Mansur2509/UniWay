import type { LocaleCode } from "../config";
import type { TranslationDictionary } from "../types";
import { en } from "./en";

export const defaultDictionary: TranslationDictionary = en;

export async function loadDictionary(locale: LocaleCode): Promise<TranslationDictionary> {
  switch (locale) {
    case "ru":
      return (await import("./ru")).ru;
    case "uz-Latn":
      return (await import("./uz-latn")).uzLatn;
    case "uz-Cyrl":
      return (await import("./uz-cyrl")).uzCyrl;
    default:
      return defaultDictionary;
  }
}
