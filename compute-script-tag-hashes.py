import hashlib
import base64

scriptContent = """
      // ENV = 'production' => DEBUG = False, else TRUE
      window.APP_DEBUG    =  {{ "true" if config['DEBUG'] else "false" }};
      window.APP_LANGUAGE = "{{ curLg }}";
    """.strip()

hashDigest = hashlib.sha256(scriptContent.encode("utf-8")).digest()
cspHash = base64.b64encode(hashDigest).decode("utf-8")

print("sha256-" + cspHash)
