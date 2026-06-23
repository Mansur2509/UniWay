import { admissionsV1En } from "./admissions-v1.en";

export const admissionsV1UzCyrl = {
  ...admissionsV1En,
  "admissions.proposals.title": "Жонли қабул тавсиялари",
  "admissions.classes.add": "Курсни қўшиш",
  "admissions.classes.added": "Қўшилди",
  "admissions.assessment.title": "Мутахассислик ва касб қизиқиш тести",
  "admissions.assessment.next": "Кейинги бўлим",
  "admissions.assessment.previous": "Олдинги бўлим",
  "admissions.assessment.results": "Тавсияларни кўриш",
  "admissions.assessment.use": "Танланган тавсиялардан фойдаланиш",
  "admissions.country.title": "Мақсад мамлакатлар",
  "admissions.readiness.title": "Ариза тайёрлиги",
  "admissions.readiness.disclaimer": "EduVerse қабулни кафолатламайди. Тайёрлик мавжуд профил маълумотлари ва мавжуд бўлса эълон қилинган диапазонларга асосланган ахборот таққослашидир.",
  "dashboard.learning.title": "Тавсия этилган ўқиш йўли",
  "events.map.title": "Имкониятлар харитаси"
} satisfies Record<keyof typeof admissionsV1En, string>;
