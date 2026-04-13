# ============================================================
#  TD Corner Pin Remote Setup
#  TouchDesigner 2023.x 이상 (2025.32460 확인)
#
#  사용법:
#    1. TouchDesigner Textport (Alt+G) 열기
#    2. 이 파일 전체 내용 붙여넣기 → Enter
#    3. 핸드폰 브라우저에서 http://[PC_IP]:9981 접속
#
#  생성 노드:
#    /project1/cornerpin1          Corner Pin TOP
#    /project1/cornerpin_server1   Web Server DAT  (port 9981)
#    /project1/cornerpin_callbacks1 Text DAT (HTML + callback)
# ============================================================

import re

TARGET = '/project1'   # 생성할 컨테이너 경로
PORT   = 9981          # 웹 서버 포트 (기존 webserver와 충돌 시 변경)
CP_OP  = 'cornerpin1' # Corner Pin TOP 이름

# ── HTML (핸드폰 UI) ─────────────────────────────────────────
_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta charset="UTF-8">
<title>Corner Pin Remote</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0;background:#0c0f14;color:#eef2f7;font-family:Arial,sans-serif}
body{padding:12px}
.wrap{max-width:760px;margin:0 auto}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;margin-bottom:12px;background:#141923;border:1px solid #252d3a;border-radius:14px}
.title{font-size:13px;letter-spacing:2px;color:#9fb5d8;font-weight:700}
.status{font-size:11px;color:#74d99a;font-weight:700}
.cornerTabs{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
.cornerTab{border:none;border-radius:12px;background:#1a202b;color:#c8d2e3;padding:14px 10px;font-size:12px;font-weight:700;border:1px solid #293243;cursor:pointer}
.cornerTab.active{background:#2aa8ff;color:#08111a;border-color:#2aa8ff;box-shadow:0 0 0 1px rgba(42,168,255,.2),0 0 18px rgba(42,168,255,.15)}
.panel{background:#141923;border:1px solid #252d3a;border-radius:16px;padding:14px;margin-bottom:12px}
.panel h2{margin:0 0 12px 0;font-size:13px;letter-spacing:1px;color:#6fc4ff}
.xyGrid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.axisCard{background:#1a202b;border:1px solid #293243;border-radius:14px;padding:12px}
.axisHead{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.axisLabel{font-size:12px;color:#94a3ba;font-weight:700}
.axisValue{font-size:22px;color:#fff;font-weight:800;letter-spacing:.5px}
.wheel{position:relative;height:110px;border-radius:14px;background:linear-gradient(180deg,#0f131a 0%,#1a212c 50%,#0f131a 100%);border:1px solid #313b4d;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;touch-action:none;user-select:none;-webkit-user-select:none;cursor:ns-resize}
.wheel.active{box-shadow:0 0 0 1px rgba(42,168,255,.28),0 0 18px rgba(42,168,255,.18);border-color:#2aa8ff}
.wheel::before{content:'';position:absolute;left:0;right:0;top:50%;height:36px;transform:translateY(-50%);background:rgba(42,168,255,.08);border-top:1px solid rgba(42,168,255,.18);border-bottom:1px solid rgba(42,168,255,.18);pointer-events:none}
.ghost{font-size:16px;color:#5f6b7f;line-height:1.2;height:22px;z-index:1}
.mainValue{font-size:30px;font-weight:800;color:#fff;line-height:1.2;height:36px;z-index:1}
.inputRow{display:grid;grid-template-columns:1fr auto auto;gap:8px;margin-top:10px}
.numInput{width:100%;height:42px;border:none;outline:none;border-radius:10px;padding:0 12px;background:#0f141c;color:#fff;font-size:16px;font-weight:700;border:1px solid #313b4d}
.smallBtn{height:42px;min-width:48px;border:none;border-radius:10px;background:#232c39;color:#eaf2ff;font-size:18px;font-weight:800;cursor:pointer}
.smallBtn:active{transform:scale(.98)}
.rowHint{margin-top:8px;font-size:10px;color:#718099;text-align:center;line-height:1.4}
.summary{background:#141923;border:1px solid #252d3a;border-radius:16px;padding:14px}
.summary h3{margin:0 0 10px 0;font-size:12px;color:#8fa4c5;letter-spacing:1px}
.coordGrid{display:grid;grid-template-columns:1fr 1fr;gap:8px 12px}
.coordItem{background:#1a202b;border:1px solid #293243;border-radius:10px;padding:10px;font-size:12px;color:#d7dfec}
.coordItem .name{font-size:10px;color:#8ea0ba;margin-bottom:4px}
.toolbar{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
.actionBtn{height:44px;border:none;border-radius:12px;background:#1f2733;color:#fff;font-size:13px;font-weight:700;cursor:pointer}
.actionBtn.primary{background:#2aa8ff;color:#08111a}
.footer{margin-top:8px;font-size:10px;color:#66758d;text-align:right}
@media(max-width:640px){.xyGrid{grid-template-columns:1fr}.coordGrid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <div class="title">CORNER PIN REMOTE</div>
    <div class="status" id="status">READY</div>
  </div>
  <div class="cornerTabs">
    <button class="cornerTab active" data-corner="tl">TOP LEFT</button>
    <button class="cornerTab" data-corner="tr">TOP RIGHT</button>
    <button class="cornerTab" data-corner="bl">BOTTOM LEFT</button>
    <button class="cornerTab" data-corner="br">BOTTOM RIGHT</button>
  </div>
  <div class="panel">
    <h2 id="panelTitle">TOP LEFT</h2>
    <div class="xyGrid">
      <div class="axisCard">
        <div class="axisHead"><div class="axisLabel">X</div><div class="axisValue" id="label_x">0.000</div></div>
        <div class="wheel" id="wheel_x">
          <div class="ghost" id="x_prev">-0.001</div>
          <div class="mainValue" id="x_main">0.000</div>
          <div class="ghost" id="x_next">0.001</div>
        </div>
        <div class="inputRow">
          <input class="numInput" id="input_x" type="number" min="-0.5" max="1.5" step="0.001" value="0.000">
          <button class="smallBtn" id="btn_x_minus">-</button>
          <button class="smallBtn" id="btn_x_plus">+</button>
        </div>
        <div class="rowHint">위/아래 드래그 | 천천히=미세 / 빠르게=큰폭</div>
      </div>
      <div class="axisCard">
        <div class="axisHead"><div class="axisLabel">Y</div><div class="axisValue" id="label_y">0.000</div></div>
        <div class="wheel" id="wheel_y">
          <div class="ghost" id="y_prev">-0.001</div>
          <div class="mainValue" id="y_main">0.000</div>
          <div class="ghost" id="y_next">0.001</div>
        </div>
        <div class="inputRow">
          <input class="numInput" id="input_y" type="number" min="-0.5" max="1.5" step="0.001" value="0.000">
          <button class="smallBtn" id="btn_y_minus">-</button>
          <button class="smallBtn" id="btn_y_plus">+</button>
        </div>
        <div class="rowHint">숫자 직접 입력 후 Enter | 포커스 아웃 적용</div>
      </div>
    </div>
    <div class="toolbar">
      <button class="actionBtn" id="btnResetSelected">RESET SELECTED</button>
      <button class="actionBtn primary" id="btnRefresh">REFRESH</button>
    </div>
  </div>
  <div class="summary">
    <h3>ALL CORNERS</h3>
    <div class="coordGrid">
      <div class="coordItem"><div class="name">TOP LEFT</div><div id="sum_tl">X 0.000 / Y 0.000</div></div>
      <div class="coordItem"><div class="name">TOP RIGHT</div><div id="sum_tr">X 1.000 / Y 0.000</div></div>
      <div class="coordItem"><div class="name">BOTTOM LEFT</div><div id="sum_bl">X 0.000 / Y 1.000</div></div>
      <div class="coordItem"><div class="name">BOTTOM RIGHT</div><div id="sum_br">X 1.000 / Y 1.000</div></div>
    </div>
    <div class="toolbar">
      <button class="actionBtn" id="btnResetAll">RESET ALL</button>
      <button class="actionBtn primary" id="btnApplyInputs">APPLY INPUTS</button>
    </div>
    <div class="footer" id="updated">LAST UPDATE: -</div>
  </div>
</div>
<script>
const defaults={tl_x:0,tl_y:0,tr_x:1,tr_y:0,bl_x:0,bl_y:1,br_x:1,br_y:1};
const values={...defaults};
const cornerNames={tl:'TOP LEFT',tr:'TOP RIGHT',bl:'BOTTOM LEFT',br:'BOTTOM RIGHT'};
let selectedCorner='tl';
function $(id){return document.getElementById(id);}
function setStatus(msg){$('status').innerText=msg;}
function nowText(){return new Date().toLocaleTimeString();}
function clamp(v,min=-0.5,max=1.5){return Math.max(min,Math.min(max,v));}
function fixed3(v){return Number(v).toFixed(3);}
function keyOf(axis){return selectedCorner+'_'+axis;}
function speedToStep(speed){
  if(speed<0.10)return 0.001;if(speed<0.22)return 0.002;
  if(speed<0.45)return 0.005;if(speed<0.90)return 0.010;
  if(speed<1.60)return 0.020;return 0.050;
}
function updateSummary(){
  $('sum_tl').innerText='X '+fixed3(values.tl_x)+' / Y '+fixed3(values.tl_y);
  $('sum_tr').innerText='X '+fixed3(values.tr_x)+' / Y '+fixed3(values.tr_y);
  $('sum_bl').innerText='X '+fixed3(values.bl_x)+' / Y '+fixed3(values.bl_y);
  $('sum_br').innerText='X '+fixed3(values.br_x)+' / Y '+fixed3(values.br_y);
  $('updated').innerText='LAST UPDATE: '+nowText();
}
function renderAxis(axis){
  const key=keyOf(axis);const val=values[key];
  $('label_'+axis).innerText=fixed3(val);
  $(axis+'_main').innerText=fixed3(val);
  $(axis+'_prev').innerText=fixed3(clamp(val-0.001));
  $(axis+'_next').innerText=fixed3(clamp(val+0.001));
  $('input_'+axis).value=fixed3(val);
}
function renderSelectedCorner(){
  $('panelTitle').innerText=cornerNames[selectedCorner];
  renderAxis('x');renderAxis('y');
  document.querySelectorAll('.cornerTab').forEach(function(btn){
    btn.classList.toggle('active',btn.dataset.corner===selectedCorner);
  });
  updateSummary();
}
function applyValue(key,val,sendNow){
  values[key]=clamp(parseFloat(val));
  if(key===keyOf('x'))renderAxis('x');
  if(key===keyOf('y'))renderAxis('y');
  updateSummary();
  if(sendNow!==false)throttledSend(key,values[key]);
}
function send(key,val){
  setStatus('SENDING');
  fetch('/set?key='+encodeURIComponent(key)+'&val='+encodeURIComponent(fixed3(val)))
    .then(function(){setStatus('READY');}).catch(function(){setStatus('ERROR');});
}
function throttle(fn,delay){
  var last=0,timer=null;
  return function(){
    var args=arguments,ctx=this,now=Date.now();
    if(now-last>=delay){last=now;fn.apply(ctx,args);}
    else{clearTimeout(timer);timer=setTimeout(function(){last=Date.now();fn.apply(ctx,args);},delay-(now-last));}
  };
}
var throttledSend=throttle(send,35);
function attachWheel(axis){
  var el=$('wheel_'+axis);
  var dragging=false,lastY=0,lastTime=0;
  el.addEventListener('pointerdown',function(e){
    dragging=true;lastY=e.clientY;lastTime=performance.now();
    el.classList.add('active');el.setPointerCapture(e.pointerId);
  });
  el.addEventListener('pointermove',function(e){
    if(!dragging)return;
    var now=performance.now();var dy=e.clientY-lastY;var dt=Math.max(1,now-lastTime);
    if(Math.abs(dy)<1)return;
    var speed=Math.abs(dy)/dt;var step=speedToStep(speed);
    var multiplier=Math.max(1,Math.floor(Math.abs(dy)/6));
    var delta=-Math.sign(dy)*step*multiplier;
    var key=keyOf(axis);applyValue(key,values[key]+delta,true);
    lastY=e.clientY;lastTime=now;
  });
  function endDrag(){dragging=false;el.classList.remove('active');}
  el.addEventListener('pointerup',endDrag);el.addEventListener('pointercancel',endDrag);
}
function bindInputs(axis){
  var input=$('input_'+axis);
  function commit(){var raw=parseFloat(input.value);if(isNaN(raw)){renderAxis(axis);return;}applyValue(keyOf(axis),raw,true);}
  input.addEventListener('change',commit);input.addEventListener('blur',commit);
  input.addEventListener('keydown',function(e){if(e.key==='Enter')input.blur();});
  $('btn_'+axis+'_minus').addEventListener('click',function(){applyValue(keyOf(axis),values[keyOf(axis)]-0.001,true);});
  $('btn_'+axis+'_plus').addEventListener('click',function(){applyValue(keyOf(axis),values[keyOf(axis)]+0.001,true);});
}
document.querySelectorAll('.cornerTab').forEach(function(btn){
  btn.addEventListener('click',function(){selectedCorner=btn.dataset.corner;renderSelectedCorner();});
});
$('btnResetSelected').addEventListener('click',function(){
  applyValue(selectedCorner+'_x',defaults[selectedCorner+'_x'],true);
  applyValue(selectedCorner+'_y',defaults[selectedCorner+'_y'],true);
});
$('btnResetAll').addEventListener('click',function(){
  Object.keys(defaults).forEach(function(key){values[key]=defaults[key];send(key,values[key]);});
  renderSelectedCorner();updateSummary();
});
$('btnApplyInputs').addEventListener('click',function(){
  ['x','y'].forEach(function(axis){var raw=parseFloat($('input_'+axis).value);if(!isNaN(raw))applyValue(keyOf(axis),raw,true);});
});
$('btnRefresh').addEventListener('click',loadState);
function loadState(){
  setStatus('LOADING');
  fetch('/state').then(function(res){
    if(!res.ok)throw new Error('no state');
    return res.json();
  }).then(function(data){
    Object.keys(defaults).forEach(function(key){
      if(data[key]!==undefined&&!isNaN(parseFloat(data[key]))){values[key]=clamp(parseFloat(data[key]));}
    });
    renderSelectedCorner();updateSummary();setStatus('READY');
  }).catch(function(){renderSelectedCorner();updateSummary();setStatus('READY');});
}
attachWheel('x');attachWheel('y');bindInputs('x');bindInputs('y');loadState();
</script>
</body>
</html>"""

# ── Callback DAT 코드 ────────────────────────────────────────
_CALLBACK = '''import json

HTML = """''' + _HTML.replace('\\', '\\\\').replace('"""', '\\"\\"\\"') + '''"""

def onHTTPRequest(webServerDAT, request, response):
    uri = request['uri']
    cp  = op('''' + CP_OP + '''')

    if uri == '/state':
        state = {
            'tl_x': cp.par.pintopleftx.val,
            'tl_y': cp.par.pintoplefty.val,
            'tr_x': cp.par.pintoprightx.val,
            'tr_y': cp.par.pintoprighty.val,
            'bl_x': cp.par.pinbotleftx.val,
            'bl_y': cp.par.pinbotlefty.val,
            'br_x': cp.par.pinbotrightx.val,
            'br_y': cp.par.pinbotrighty.val,
        }
        response['statusCode'] = 200
        response['data'] = json.dumps(state)
        return response

    if uri == '/set':
        args = request['pars']
        key  = args.get('key', '')
        val  = float(args.get('val', 0))
        if   key == 'tl_x': cp.par.pintopleftx  = val
        elif key == 'tl_y': cp.par.pintoplefty  = val
        elif key == 'tr_x': cp.par.pintoprightx = val
        elif key == 'tr_y': cp.par.pintoprighty = val
        elif key == 'bl_x': cp.par.pinbotleftx  = val
        elif key == 'bl_y': cp.par.pinbotlefty  = val
        elif key == 'br_x': cp.par.pinbotrightx = val
        elif key == 'br_y': cp.par.pinbotrighty = val
        response['statusCode'] = 200
        response['data'] = 'ok'
        return response

    response['statusCode'] = 200
    response['data'] = HTML
    return response
'''

# ── 노드 생성 ────────────────────────────────────────────────
def _remove_existing(root):
    for name in ['cornerpin1', 'cornerpin_server1', 'cornerpin_callbacks1']:
        o = root.findChildren(name=name, maxDepth=1)
        for n in o:
            n.destroy()

def setup():
    root = op(TARGET)

    print('[cornerpin] 기존 노드 제거 중...')
    _remove_existing(root)

    # 1. Corner Pin TOP
    cp = root.create(cornerPinTOP, CP_OP)
    cp.nodeX = 0
    cp.nodeY = 0
    print('[cornerpin] cornerpin1 생성 완료')

    # 2. Web Server DAT
    ws = root.create(webserverDAT, 'cornerpin_server1')
    ws.nodeX = -300
    ws.nodeY = -200
    ws.par.port   = PORT
    ws.par.active = 1
    print('[cornerpin] cornerpin_server1 생성 완료 (port {})'.format(PORT))

    # 3. Callback Text DAT
    cb = root.create(textDAT, 'cornerpin_callbacks1')
    cb.nodeX = 100
    cb.nodeY = -200
    cb.par.language = 'python'
    cb.text = _CALLBACK
    ws.par.callbacks = cb
    print('[cornerpin] cornerpin_callbacks1 생성 완료')

    print('')
    print('====================================')
    print('  설정 완료!')
    print('  http://[PC_IP]:{} 접속'.format(PORT))
    print('  cornerpin1 을 콘텐츠 소스에 연결하세요')
    print('====================================')

setup()
