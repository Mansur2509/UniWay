// Hand-picked, real university names confirmed against the live production
// /universities catalog (454 universities at the time this was written).
// Deliberately a static constant rather than an API call: the marketing
// landing page must render without any backend dependency, given the
// Render free-tier's 60-90s cold start. Re-verify this list against
// production data if it's revisited later.
export const MARQUEE_UNIVERSITIES: readonly string[] = [
  "Harvard University",
  "Cornell University",
  "Columbia University",
  "Duke University",
  "Brown University",
  "Dartmouth College",
  "Carnegie Mellon University",
  "Georgetown University",
  "Imperial College London",
  "Australian National University (ANU)",
  "Boston University (BU)",
  "Al-Farabi Kazakh National University",
  "Bocconi University",
  "Fudan University",
  "HSE University",
  "Heidelberg University",
  "Chulalongkorn University",
  "City University of Hong Kong (CityUHK)",
  "American University of Sharjah",
  "Arizona State University",
  "Deakin University",
  "Ghent University"
];
