import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(scriptDirectory, "..");
const sourceRoot = path.join(frontendRoot, "src");
const dictionaryDirectory = path.join(sourceRoot, "shared", "i18n", "dictionaries");
const dictionaryFiles = {
  en: ["en.ts", "beta-preview.en.ts", "onboarding.en.ts", "admissions-v1.en.ts"],
  ru: ["ru.ts", "beta-preview.ru.ts", "onboarding.ru.ts", "admissions-v1.en.ts"],
  "uz-Latn": ["uz-latn.ts", "beta-preview.uz-latn.ts", "onboarding.en.ts", "admissions-v1.en.ts"],
  "uz-Cyrl": ["uz-cyrl.ts", "beta-preview.uz-cyrl.ts", "onboarding.en.ts", "admissions-v1.en.ts"]
};

function readKeys(filenames) {
  return filenames.flatMap((filename) => {
    const source = fs.readFileSync(path.join(dictionaryDirectory, filename), "utf8");
    return [...source.matchAll(/^\s*"([^"]+)"\s*:/gm)].map((match) => match[1]);
  });
}

function collectTypeScriptFiles(directory, files = []) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      collectTypeScriptFiles(fullPath, files);
    } else if (/\.(ts|tsx)$/.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

const englishKeys = readKeys(dictionaryFiles.en);
const englishKeySet = new Set(englishKeys);

if (englishKeys.length !== englishKeySet.size) {
  throw new Error("The English dictionary contains duplicate keys.");
}

for (const [locale, filename] of Object.entries(dictionaryFiles)) {
  const localeKeys = readKeys(filename);
  const localeKeySet = new Set(localeKeys);
  const missingKeys = englishKeys.filter((key) => !localeKeySet.has(key));
  const extraKeys = localeKeys.filter((key) => !englishKeySet.has(key));

  if (
    localeKeys.length !== localeKeySet.size ||
    missingKeys.length > 0 ||
    extraKeys.length > 0
  ) {
    throw new Error(
      `${locale}: missing=[${missingKeys.join(", ")}] extra=[${extraKeys.join(", ")}]`
    );
  }
}

const unknownUsages = [];
const translationCallPattern = /\bt\(\s*["']([^"']+)["']/g;

for (const filename of collectTypeScriptFiles(sourceRoot)) {
  const source = fs.readFileSync(filename, "utf8");
  for (const match of source.matchAll(translationCallPattern)) {
    if (!englishKeySet.has(match[1])) {
      unknownUsages.push(`${path.relative(sourceRoot, filename)}: ${match[1]}`);
    }
  }
}

if (unknownUsages.length > 0) {
  throw new Error(`Unknown translation keys:\n${unknownUsages.join("\n")}`);
}

console.log(
  `i18n check passed: ${englishKeys.length} keys across ${Object.keys(dictionaryFiles).length} locales.`
);
