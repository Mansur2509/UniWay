import type { LocaleCode } from "../config";
import type { TranslationDictionary } from "../types";
import { en } from "./en";
import { ru } from "./ru";
import { uzCyrl } from "./uz-cyrl";
import { uzLatn } from "./uz-latn";

export const dictionaries: Record<LocaleCode, TranslationDictionary> = {
  en,
  ru,
  "uz-Latn": uzLatn,
  "uz-Cyrl": uzCyrl
};

