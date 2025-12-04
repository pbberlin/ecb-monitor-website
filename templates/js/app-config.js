// ENV = 'production' => DEBUG = False, else TRUE
window.APP_DEBUG    =  {{ "true" if debug else "false" }};
window.APP_LANGUAGE = "{{ curLg }}";
console.log(`javascript lang is ${window.APP_LANGUAGE}`)
