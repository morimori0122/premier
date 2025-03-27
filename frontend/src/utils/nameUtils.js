export const getFullName = (shortName) => {
  const nameMap = {
    "Arsenal Football Club": "Arsenal",
    "Association Football Club Bournemouth": "Bournemouth",
    "Aston Villa Football Club": "Aston Villa",
    "Brentford Football Club": "Brentford",
    "Brighton and Hove Albion Football Club": "Brighton",
    "Chelsea Football Club": "Chelsea",
    "Crystal Palace Football Club": "Crystal Palace",
    "Everton Football Club": "Everton",
    "Fulham Football Club": "Fulham",
    "Ipswich Town Football Club": "Ipswich",
    "Leicester City Football Club": "Leicester",
    "Liverpool Football Club": "Liverpool",
    "Manchester City Football Club": "Manchester City",
    "Manchester United Football Club": "Manchester United",
    "Newcastle United Football Club": "Newcastle",
    "Nottingham Forest Football Club": "Nottingham Forest",
    "Southampton Football Club": "Southampton",
    "Tottenham Hotspur Football Club": "Tottenham",
    "West Ham United Football Club": "West Ham",
    "Wolverhampton Wanderers Football Club": "Wolves"
  };

  // 正規化関数（記号・FC等を削除して比較）
  const normalize = (str) =>
    str
      .toLowerCase()
      .replace(/football club|fc|afc/gi, "")
      .replace(/&/g, "and")
      .replace(/[^a-z\s]/gi, "")
      .replace(/\s+/g, " ")
      .trim();

  const normalizedInput = normalize(shortName);

  for (const [full, short] of Object.entries(nameMap)) {
    if (
      normalize(full) === normalizedInput ||
      normalize(short) === normalizedInput
    ) {
      return full;
    }
  }

  console.warn(`⚠️ 変換失敗: ${shortName} は正式名称に一致しませんでした`);
  return shortName; // fallback
};
