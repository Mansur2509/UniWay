import type { TranslationKey } from "@/shared/i18n";

import type { MajorCategoryId } from "./major-catalog";

export const targetCountries = [
  "United States",
  "United Kingdom",
  "China",
  "Germany",
  "Italy",
  "South Korea",
  "Canada",
  "France",
  "Netherlands",
  "Hong Kong",
  "Japan",
  "Singapore",
  "United Arab Emirates",
  "Uzbekistan",
  "Kazakhstan",
  "Kyrgyzstan",
  "Tajikistan",
  "Turkey"
] as const;

export type RecommendedClassId =
  | "satMath"
  | "satReadingWriting"
  | "ieltsReading"
  | "ieltsWriting"
  | "ieltsSpeaking"
  | "ieltsListening"
  | "apCalculus"
  | "apMicroeconomics"
  | "apMacroeconomics"
  | "apComputerScience"
  | "apPhysics"
  | "apBiology"
  | "apChemistry"
  | "financeLiteracy"
  | "researchBasics"
  | "essayWriting"
  | "munDebate"
  | "portfolioBuilding";

export type RecommendedClass = {
  id: RecommendedClassId;
  value: string;
  labelKey: TranslationKey;
};

export const classCatalog: RecommendedClass[] = [
  ["satMath", "SAT Math", "admissions.class.satMath"],
  ["satReadingWriting", "SAT Reading and Writing", "admissions.class.satReadingWriting"],
  ["ieltsReading", "IELTS Reading", "admissions.class.ieltsReading"],
  ["ieltsWriting", "IELTS Writing", "admissions.class.ieltsWriting"],
  ["ieltsSpeaking", "IELTS Speaking", "admissions.class.ieltsSpeaking"],
  ["ieltsListening", "IELTS Listening", "admissions.class.ieltsListening"],
  ["apCalculus", "AP Calculus", "admissions.class.apCalculus"],
  ["apMicroeconomics", "AP Microeconomics", "admissions.class.apMicroeconomics"],
  ["apMacroeconomics", "AP Macroeconomics", "admissions.class.apMacroeconomics"],
  ["apComputerScience", "AP Computer Science", "admissions.class.apComputerScience"],
  ["apPhysics", "AP Physics", "admissions.class.apPhysics"],
  ["apBiology", "AP Biology", "admissions.class.apBiology"],
  ["apChemistry", "AP Chemistry", "admissions.class.apChemistry"],
  ["financeLiteracy", "Finance Literacy Basics", "admissions.class.financeLiteracy"],
  ["researchBasics", "Research Basics", "admissions.class.researchBasics"],
  ["essayWriting", "Essay Writing Basics", "admissions.class.essayWriting"],
  ["munDebate", "MUN and Debate Preparation", "admissions.class.munDebate"],
  ["portfolioBuilding", "Portfolio Building", "admissions.class.portfolioBuilding"]
].map(([id, value, labelKey]) => ({
  id: id as RecommendedClassId,
  value,
  labelKey: labelKey as TranslationKey
}));

export const clusterClassMap: Record<MajorCategoryId, RecommendedClassId[]> = {
  business: ["apMicroeconomics", "apMacroeconomics", "satMath", "financeLiteracy"],
  computing: ["apComputerScience", "apCalculus", "satMath", "researchBasics"],
  engineering: ["apCalculus", "apPhysics", "satMath", "portfolioBuilding"],
  mathematics: ["apCalculus", "satMath", "researchBasics"],
  naturalSciences: ["apBiology", "apChemistry", "apPhysics", "researchBasics"],
  health: ["apBiology", "apChemistry", "researchBasics"],
  socialSciences: ["satReadingWriting", "essayWriting", "researchBasics"],
  lawPolicy: ["satReadingWriting", "essayWriting", "munDebate"],
  humanities: ["satReadingWriting", "essayWriting", "portfolioBuilding"],
  media: ["essayWriting", "portfolioBuilding", "satReadingWriting"],
  artsDesign: ["portfolioBuilding", "essayWriting"],
  education: ["satReadingWriting", "researchBasics"],
  environment: ["apBiology", "apChemistry", "researchBasics"],
  agriculture: ["apBiology", "apChemistry", "financeLiteracy"],
  interdisciplinary: ["researchBasics", "essayWriting", "satMath", "portfolioBuilding"]
};

export const clusterEventKeys: Record<MajorCategoryId, TranslationKey[]> = {
  business: ["admissions.event.businessCompetition", "admissions.event.economicsForum"],
  computing: ["admissions.event.hackathon", "admissions.event.codingWorkshop"],
  engineering: ["admissions.event.robotics", "admissions.event.engineeringProject"],
  mathematics: ["admissions.event.olympiad", "admissions.event.dataWorkshop"],
  naturalSciences: ["admissions.event.scienceFair", "admissions.event.research"],
  health: ["admissions.event.healthVolunteering", "admissions.event.research"],
  socialSciences: ["admissions.event.communityResearch", "admissions.event.mun"],
  lawPolicy: ["admissions.event.mun", "admissions.event.debate"],
  humanities: ["admissions.event.writing", "admissions.event.culture"],
  media: ["admissions.event.journalism", "admissions.event.portfolio"],
  artsDesign: ["admissions.event.portfolio", "admissions.event.design"],
  education: ["admissions.event.volunteering", "admissions.event.workshop"],
  environment: ["admissions.event.sustainability", "admissions.event.research"],
  agriculture: ["admissions.event.sustainability", "admissions.event.scienceFair"],
  interdisciplinary: ["admissions.event.research", "admissions.event.innovation"]
};
