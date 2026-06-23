import type { en } from "./dictionaries/en";

export type TranslationKey = keyof typeof en;
export type TranslationDictionary = Record<TranslationKey, string>;
export type TranslationValues = Record<string, string | number>;

