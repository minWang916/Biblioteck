const languages = [
  "Afrikaans",
  "Albanian",
  "Amharic",
  "Arabic",
  "Aragonese",
  "Armenian",
  "Asturian",
  "Azerbaijani",
  "Basque",
  "Belarusian",
  "Bengali",
  "Bosnian",
  "Breton",
  "Bulgarian",
  "Catalan",
  "Central Kurdish",
  "Chinese",
  "Chinese (Hong Kong)",
  "Chinese (Simplified)",
  "Chinese (Traditional)",
  "Corsican",
  "Croatian",
  "Czech",
  "Danish",
  "Dutch",
  "English",
  "English (Australia)",
  "English (Canada)",
  "English (India)",
  "English (New Zealand)",
  "English (South Africa)",
  "English (United Kingdom)",
  "English (United States)",
  "Esperanto",
  "Estonian",
  "Faroese",
  "Filipino",
  "Finnish",
  "French",
  "French (Canada)",
  "French (France)",
  "French (Switzerland)",
  "Galician",
  "Georgian",
  "German",
  "German (Austria)",
  "German (Germany)",
  "German (Liechtenstein)",
  "German (Switzerland)",
  "Greek",
  "Guarani",
  "Gujarati",
  "Hausa",
  "Hawaiian",
  "Hebrew",
  "Hindi",
  "Hungarian",
  "Icelandic",
  "Indonesian",
  "Interlingua",
  "Irish",
  "Italian",
  "Italian (Italy)",
  "Italian (Switzerland)",
  "Japanese",
  "Kannada",
  "Kazakh",
  "Khmer",
  "Korean",
  "Kurdish",
  "Kyrgyz",
  "Lao",
  "Latin",
  "Latvian",
  "Lingala",
  "Lithuanian",
  "Macedonian",
  "Malay",
  "Malayalam",
  "Maltese",
  "Marathi",
  "Mongolian",
  "Nepali",
  "Norwegian",
  "Norwegian Bokmål",
  "Norwegian Nynorsk",
  "Occitan",
  "Oriya",
  "Oromo",
  "Pashto",
  "Persian",
  "Polish",
  "Portuguese",
  "Portuguese (Brazil)",
  "Portuguese (Portugal)",
  "Punjabi",
  "Quechua",
  "Romanian",
  "Romanian (Moldova)",
  "Romansh",
  "Russian",
  "Scottish Gaelic",
  "Serbian",
  "Serbo",
  "Shona",
  "Sindhi",
  "Sinhala",
  "Slovak",
  "Slovenian",
  "Somali",
  "Southern Sotho",
  "Spanish",
  "Spanish (Argentina)",
  "Spanish (Latin America)",
  "Spanish (Mexico)",
  "Spanish (Spain)",
  "Spanish (United States)",
  "Sundanese",
  "Swahili",
  "Swedish",
  "Tajik",
  "Tamil",
  "Tatar",
  "Telugu",
  "Thai",
  "Tigrinya",
  "Tongan",
  "Turkish",
  "Turkmen",
  "Twi",
  "Ukrainian",
  "Urdu",
  "Uyghur",
  "Uzbek",
  "Vietnamese",
  "Walloon",
  "Welsh",
  "Western Frisian",
  "Xhosa",
  "Yiddish",
  "Yoruba",
  "Zulu"
  ];
function generateLanguages() {
  const selectLanguage = document.getElementById('language');
  languages.forEach((language) => {
      const option = document.createElement('option');
      option.value = language;
      option.text = language;
      selectLanguage.appendChild(option);
  });
}
generateLanguages();

function validateLanguage() {
  const selectedLanguage = document.getElementById('language').value;
  if (!selectedLanguage) {
      alert('Please select a language.');
      return false;
  }
  return true;
}

function generateYears() {
  const selectElement = document.getElementById('publication');
  const currentYear = new Date().getFullYear();
  const startYear = 1900;
  const endYear = 2024;
  for (let year = endYear; year >= startYear; year--) {
      const option = document.createElement('option');
      option.value = year;
      option.text = year;
      selectElement.appendChild(option);
  }
}
// Call the function to generate years
generateYears();

function validateYear() {
  const selectedYear = document.getElementById('publication').value;
  if (!selectedYear) {
      alert('Please select a year.');
  return false;
  }
  return true;
}