import sys
from playwright.sync_api import sync_playwright
out = sys.argv[1]
JS = """async () => {
  const U=window.__ui; U.configureAppUI("test");
  const A=[{sign:"คุณ",conf:.92,face:{seen:true}},{sign:"ต้องการ",conf:.9,face:{seen:true,question:true}},{sign:"ยา",conf:.88,face:{seen:true}}];
  const Bw=[{sign:"ฉัน",conf:.9,face:{seen:true}},{sign:"ต้องการ",conf:.9,face:{seen:true,negative:true}},{sign:"ยา",conf:.88,face:{seen:true}}];
  U.setBuf(A.slice()); U.renderWordRow(); await U.finishSentence();
  U.setBuf(Bw.slice()); U.renderWordRow(); await U.finishSentence();
  U.setBuf(Bw.slice()); U.renderWordRow();
  return document.getElementById("sentence").textContent;
}"""
HTML = open("innovation/web_app/index.html", encoding="utf-8").read()
i = HTML.rindex("</script>")
HTML = HTML[:i] + "window.__ui={configureAppUI,finishSentence,renderWordRow,setBuf:(a)=>{wordBuffer=a;}};" + HTML[i:]   # in-memory only: lets the script drive the module code
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1360, "height": 900}, device_scale_factor=2)
    pg.route("**/index.html", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=HTML))
    pg.goto("http://localhost:8765/index.html", wait_until="domcontentloaded"); pg.wait_for_timeout(3500)
    print("sentence:", pg.evaluate(JS)); pg.wait_for_timeout(600)
    pg.locator("#composerCard").screenshot(path=out + "/composer.png")
    pg.locator("#bridgeSide").screenshot(path=out + "/side.png")
    # face-reading settings (collapsed section at the bottom left)
    try:
        pg.get_by_text("ตั้งค่าการอ่านสีหน้า").first.click(); pg.wait_for_timeout(500)
        box = pg.get_by_text("ตั้งค่าการอ่านสีหน้า").first.locator("xpath=ancestor::*[self::details or self::section or self::div][1]")
        box.screenshot(path=out + "/facesettings.png")
    except Exception as e: print("settings crop failed:", str(e)[:120])
    b.close()
