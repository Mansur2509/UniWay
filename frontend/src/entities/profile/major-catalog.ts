import type { TranslationKey } from "@/shared/i18n";

export type MajorCategoryId =
  | "business"
  | "computing"
  | "engineering"
  | "mathematics"
  | "naturalSciences"
  | "health"
  | "socialSciences"
  | "lawPolicy"
  | "humanities"
  | "media"
  | "artsDesign"
  | "education"
  | "environment"
  | "agriculture"
  | "interdisciplinary";

export type MajorOption = {
  id: string;
  value: string;
  labelKey?: TranslationKey;
};

export type MajorCategory = {
  id: MajorCategoryId;
  labelKey: TranslationKey;
  majors: MajorOption[];
};

function toId(value: string) {
  return value
    .replace(/&/g, " and ")
    .replace(/[^A-Za-z0-9]+(.)/g, (_, character: string) => character.toUpperCase())
    .replace(/^[A-Z]/, (character) => character.toLowerCase());
}

function majors(...values: string[]): MajorOption[] {
  return values.map((value) => ({ id: toId(value), value }));
}

export const majorCatalog: MajorCategory[] = [
  {
    id: "business",
    labelKey: "onboarding.majorCategory.business",
    majors: majors(
      "Economics", "Business Administration", "Finance", "Accounting", "Marketing",
      "Management", "Entrepreneurship", "International Business", "Business Analytics",
      "Operations Management", "Real Estate", "Actuarial Science", "Financial Engineering",
      "Mathematical Economics", "Political Economy", "Economics and Data Science",
      "Economics and Computer Science", "Applied Economics", "Quantitative Economics"
    )
  },
  {
    id: "computing",
    labelKey: "onboarding.majorCategory.computing",
    majors: majors(
      "Computer Science", "Data Science", "Artificial Intelligence", "Machine Learning",
      "Software Engineering", "Computer Engineering", "Information Science",
      "Information Systems", "Cybersecurity", "Human-Computer Interaction",
      "Computational Biology", "Computational Linguistics", "Cognitive Science", "Robotics",
      "Statistics and Data Science", "Applied Mathematics and Computer Science",
      "Computer Science and Economics", "Computer Science and Philosophy",
      "Computer Science and Mathematics"
    )
  },
  {
    id: "engineering",
    labelKey: "onboarding.majorCategory.engineering",
    majors: majors(
      "Mechanical Engineering", "Electrical Engineering", "Computer Engineering",
      "Civil Engineering", "Chemical Engineering", "Biomedical Engineering",
      "Environmental Engineering", "Aerospace Engineering",
      "Materials Science and Engineering", "Industrial Engineering", "Systems Engineering",
      "Engineering Science", "Engineering Physics", "Operations Research",
      "Nuclear Engineering", "Petroleum Engineering", "Robotics Engineering",
      "Bioengineering", "Electrical Engineering and Computer Science",
      "Engineering Management"
    )
  },
  {
    id: "mathematics",
    labelKey: "onboarding.majorCategory.mathematics",
    majors: majors(
      "Mathematics", "Applied Mathematics", "Statistics", "Statistics and Data Science",
      "Mathematics and Computer Science", "Financial Mathematics", "Actuarial Mathematics",
      "Computational Mathematics", "Mathematical Sciences", "Quantitative Biology",
      "Operations Research", "Decision Science"
    )
  },
  {
    id: "naturalSciences",
    labelKey: "onboarding.majorCategory.naturalSciences",
    majors: majors(
      "Physics", "Astrophysics", "Astronomy", "Chemistry", "Biochemistry", "Biology",
      "Molecular Biology", "Cell Biology", "Genetics", "Neuroscience", "Cognitive Science",
      "Earth Science", "Environmental Science", "Marine Biology", "Geology", "Geophysics",
      "Ecology and Evolutionary Biology", "Atmospheric Science", "Planetary Science"
    )
  },
  {
    id: "health",
    labelKey: "onboarding.majorCategory.health",
    majors: majors(
      "Public Health", "Global Health", "Health Policy", "Human Biology", "Neuroscience",
      "Biomedical Sciences", "Biology", "Biochemistry", "Nutrition Science", "Kinesiology",
      "Exercise Science", "Pre-Med Track", "Health and Society", "Medical Anthropology",
      "Bioethics"
    )
  },
  {
    id: "socialSciences",
    labelKey: "onboarding.majorCategory.socialSciences",
    majors: majors(
      "Psychology", "Sociology", "Political Science", "International Relations",
      "Government", "Public Policy", "Social Policy", "Anthropology", "Geography",
      "Urban Studies", "Criminology", "Gender Studies", "Global Studies",
      "Peace and Conflict Studies", "Regional Studies"
    )
  },
  {
    id: "lawPolicy",
    labelKey: "onboarding.majorCategory.lawPolicy",
    majors: majors(
      "Political Science", "Government", "Public Policy", "International Relations",
      "Legal Studies", "Ethics Politics and Economics", "Philosophy Politics and Economics",
      "Global Affairs", "Security Studies", "Human Rights", "Public Administration",
      "Social Policy"
    )
  },
  {
    id: "humanities",
    labelKey: "onboarding.majorCategory.humanities",
    majors: majors(
      "English", "Comparative Literature", "History", "Philosophy", "Classics",
      "Religious Studies", "Linguistics", "Modern Languages", "French", "German", "Spanish",
      "Russian", "Arabic", "Chinese", "Japanese", "Italian", "Slavic Studies",
      "Near Eastern Studies", "Medieval Studies", "American Studies", "European Studies"
    )
  },
  {
    id: "media",
    labelKey: "onboarding.majorCategory.media",
    majors: majors(
      "Communication", "Media Studies", "Journalism", "Film and Media Studies",
      "Digital Media", "Public Relations", "Advertising", "Rhetoric", "Writing",
      "Creative Writing", "Strategic Communication"
    )
  },
  {
    id: "artsDesign",
    labelKey: "onboarding.majorCategory.artsDesign",
    majors: majors(
      "Architecture", "Urban Design", "Studio Art", "Fine Arts", "Graphic Design",
      "Industrial Design", "Product Design", "Design", "Visual Arts", "Art History", "Music",
      "Theater", "Dance", "Film", "Animation", "Photography", "Game Design", "Digital Arts"
    )
  },
  {
    id: "education",
    labelKey: "onboarding.majorCategory.education",
    majors: majors(
      "Education", "Human Development", "Learning Sciences", "Child Development",
      "Education Studies", "Special Education", "Educational Psychology",
      "Teaching and Teacher Education"
    )
  },
  {
    id: "environment",
    labelKey: "onboarding.majorCategory.environment",
    majors: majors(
      "Environmental Studies", "Environmental Science", "Environmental Engineering",
      "Sustainability Studies", "Climate Science", "Earth and Planetary Sciences", "Ecology",
      "Natural Resources", "Energy Studies", "Urban and Environmental Policy",
      "Conservation Biology"
    )
  },
  {
    id: "agriculture",
    labelKey: "onboarding.majorCategory.agriculture",
    majors: majors(
      "Agricultural Science", "Food Science", "Animal Science", "Plant Science", "Nutrition",
      "Viticulture and Enology", "Natural Resources", "Agricultural Economics",
      "Environmental and Resource Economics"
    )
  },
  {
    id: "interdisciplinary",
    labelKey: "onboarding.majorCategory.interdisciplinary",
    majors: majors(
      "Cognitive Science", "Science Technology and Society", "Ethics Politics and Economics",
      "Philosophy Politics and Economics", "Symbolic Systems", "Human Biology",
      "Computational Social Science", "Social Data Science", "Behavioral Economics",
      "Innovation and Entrepreneurship", "Technology and Society", "Global Affairs",
      "International Development", "Urban Studies", "Digital Humanities"
    )
  }
];

export const recommendationSignals: Record<string, MajorCategoryId[]> = {
  math: ["mathematics", "engineering", "computing", "business"],
  science: ["naturalSciences", "health", "engineering", "environment"],
  technology: ["computing", "engineering", "interdisciplinary"],
  writing: ["humanities", "media", "lawPolicy"],
  people: ["socialSciences", "education", "health"],
  business: ["business", "lawPolicy"],
  creative: ["artsDesign", "media", "humanities"],
  environment: ["environment", "agriculture", "naturalSciences"],
  policy: ["lawPolicy", "socialSciences", "business"]
};
