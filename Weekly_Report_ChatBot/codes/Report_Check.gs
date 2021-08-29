// Global variable
var file_name = DriveApp.getFileById("{JSON File ID}").getName()
var folder = DriveApp.getFolderById("{Group Drive Folder ID}");
var except_user = "{예외 대상 Email 주소}"
var daEmails = GroupsApp.getGroupByEmail("{DA Team Group Mail}").getUsers();
var dbEmails = GroupsApp.getGroupByEmail("{DB Team Group Mail}").getUsers();
var api_url = "{API GateWay URL}";
var subject = "Data Analytics 팀 주간보고";
var weather_desc = {
  Thunderstorm : "천둥 번개네요... 이불밖은 위험한데... ㄷㄷ",
  Drizzle : "오늘은 비가 오네요. 우산들은 다들 챙기셨죠?",
  Rain : "오늘은 비가 오네요. 우산들은 다들 챙기셨죠?",
  Snow : "눈이네요 통근길 화이팅 입니다!!",
  Atmosphere : "마스크 잘 쓰고 다니세요",
  Clear : "오늘은 날씨가 맑음이랍니다. 점심 식사 후 산책 어떠세요?",
  Clouds : "오늘은 날씨가 많이 흐리네요... 오늘 업무는 상쾌한 음악과 함께 어떠실까요?"
}

// Main Process 매주 수요일 17시
function apicall() {
  Logger.log(daEmails);
  var payload = {
      "namelist" : filter_json(),
      "team" : "Data Analytics"
    };
 
  var options = {
    "method"  : "post",
    "payload" : JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  var response   = UrlFetchApp.fetch(api_url, options);   

  Logger.log(response);

  return response.getContentText();
}

// Email 주소에서 UserName 추출 후 한글로 번역
function translate_to_kor(email) {
  var temp_name = ("" + email).split("@")[0].split(".")
  var name = temp_name[1] + " " + temp_name[0]
  var translatedText = LanguageApp.translate(name, 'en', 'ko').replace(" ","");

  return translatedText
}

// Email에서 한글 이름 추출
function get_user_kor(email){
  var user = ContactsApp.getContact(email);

  // If user in contacts, return their name
  if (user) {
    // Get korean full name
    var name = user.getFullName().substring(0,3);
    Logger.log(name);
  }
  if (!name) {
    // If not in Contacts, translate to korean.
    name = translate_to_kor(email);
    Logger.log(name);
  }
  return name;
}

// 주간 보고 양식 제출하면 작성 여부 Json 파일 update
function check_weekly(event) {
  var user_mail = "" + event.values[3];

  var json_obj = read_data(folder, file_name);
  json_obj[user_mail] = "O"
  save_data(folder, file_name, json_obj);
  Logger.log(json_obj);
}

// 작성 여부 Json object를 json 파일로 지정 drive 위치에 저장
function save_data(folder, fileName, contents) {
  var filename = fileName;

  var children = folder.getFilesByName(filename);
  var file = null;
  if (children.hasNext()) {
    file = children.next();
    var jstring = Utilities.jsonStringify(contents);
    Logger.log(jstring);
    file.setContent(jstring);
  } else {
    folder.createFile(filename, contents);
  }
}

// 작성 여부 Json reset 매주 금요일 오전 10시
function reset_json() {  
  //Object literal for testing purposes
  var user_json = {}

  for (var n in daEmails) {
    user_json["" + daEmails[n]] = "X"
  }

  save_data(folder, file_name, user_json);
}

// 작성 여부 Json 파일 지정된 dirve 경로에서 read 후 Json Object로 반환
function read_data(folder, fileName) {
  var filename = fileName;

  var children = folder.getFilesByName(filename);
  var file = null;
  var json;
  if (children.hasNext()) {
    file = children.next();
    var content = file.getBlob().getDataAsString();
    json = JSON.parse(content);
    Logger.log(json);
  } else {
    json = JSON.parse("{}");
  }
  return json
}

// 작성 여부 Json에서 value가 X인 Key들 추출
function filter_json() {
  var json_obj = read_data(folder, file_name);
  var user_list = [];
  for (var user in json_obj) {
    var written = json_obj[user];
    if (written == "X" && "" + user != except_user) {
      user_list.push(get_user_kor("" + user));
    }

  }
  return user_list
}

// group에 새 member 여부 확인 매주 화요일 오전 10시
function check_new_member() {
  var json_obj = read_data(folder, file_name);
  var user_list = [];
  var new_member_list = [];
  for (var user in json_obj) {
    user_list.push("" + user);
  }

  for (var line in daEmails) {
    var isMatched = user_list.indexOf("" + daEmails[line]);
    if (isMatched == -1) {
      new_member_list.push("" + user)
    }
  }
  Logger.log(new_member_list);
  send_form_new_member(new_member_list)
}

// 새 멤버에게 양식 첨부해서 메일 보내기
function send_form_new_member(member_list) {
  var message = "해당 메일을 즐겨 찾기 등록 후 매주 수요일 18시 이전까지 작성 및 등록 합니다.\n첨부된 양식에 예시와 같이 작성 후 '보내기'클릭하면 주간보고 sheet에 자동 등록됩니다.\n주간 보고 작성 후 수정은 DMS 공유 드라이브에서 직접 수정 가능합니다.";
  var htmlTemplate  = HtmlService.createTemplateFromFile("form");
  var htmlBody = htmlTemplate.evaluate().getContent();

  for (var member in member_list) {
    
    MailApp.sendEmail({
      to: "" + member_list[member],
      subject: subject,
      htmlBody: message + htmlBody
    }); 
  }
}

function get_weather_info() {
  // Enter your API key here
  var api_key = "{Open_weather_API_KEY}"
  //  base_url variable to store url
  var base_url = "http://api.openweathermap.org/data/2.5/weather?"
  //  Give city name
  var city_name = "Seoul"
  var url = base_url + "appid=" + api_key + "&q=" + city_name // URL for weather. API key needed(free)
  var response = UrlFetchApp.fetch(url, { method: 'GET', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' } });
   
  var json = response.getContentText();
  var data = JSON.parse(json);
  var description = LanguageApp.translate(data.weather[0].description, 'en', 'ko');
  var main = LanguageApp.translate(data.weather[0].main, 'en', 'ko');
  var weather_msg;
  if (main == "Atmosphere") {
    weather_msg = main + "|" + "오늘은 " + description + " 입니다. " + weather_desc[data.weather[0].main]
  } else{
    weather_msg = main + "|" + weather_desc[data.weather[0].main]
  }
  Logger.log(weather_msg);

  return weather_msg
}

// DA Team 에만
function send_all_user() {
  var all_user_list = [];

  for (var n in daEmails) {
    if ("" + daEmails[n] != except_user) {
      all_user_list.push("" + get_user_kor("" + daEmails[n]));
    }
  }
  for (var n in dbEmails) {
    if ("" + daEmails[n] != "bumkyu.kim@bespinglobal.com") {
      all_user_list.push("" + get_user_kor("" + dbEmails[n]));
    }
  }

  var payload = {
      "namelist" : all_user_list,
      "team" : "DataOps"
    };
 
  var options = {
    "method"  : "post",
    "payload" : JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  var response = UrlFetchApp.fetch(api_url, options);
  Logger.log(response);
 
    return response.getContentText();
}