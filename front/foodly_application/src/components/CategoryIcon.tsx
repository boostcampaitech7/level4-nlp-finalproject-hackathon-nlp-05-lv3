import {
  faAppleWhole,
  faBreadSlice,
  faFireBurner,
  faPlateWheat,
  faCookieBite,
  faMugSaucer,
  faFish,
  faBowlFood,
  faCow,
  faJar,
  faEgg,
  faQuestion,
  faCarrot,
  IconDefinition
} from "@fortawesome/free-solid-svg-icons";

export const getIconForCategory = (name: string): IconDefinition => {
  const iconMapping: { [key: string]: IconDefinition } = {
    '과일': faAppleWhole,
    '과자/빙과': faCookieBite,
    '김치/반찬': faPlateWheat,
    '라면/간편식': faFireBurner,
    '베이커리/잼': faBreadSlice,
    '생수/음료/차': faMugSaucer,
    '수산/건어물': faFish,
    '쌀/잡곡/견과': faBowlFood,
    '우유/유제품': faCow,
    '장/조미료': faJar,
    '정육/계란': faEgg,
    '채소': faCarrot,
  };
  return iconMapping[name] || faQuestion;
};