using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 主界面 HUD 的体力条。
/// 优先使用场景里现成的数字文本（numText）；场景里没有体力条时，运行时用代码搭一条
/// 和钻石条同款的「药丸底 + 闪电徽章 + 数字 + 绿色加号」，不依赖场景改动。
/// 顺带每 recoverInterval 秒结算一次在线恢复，挂在主界面不动也会慢慢涨体力。
/// </summary>
public class EnergyHudText : MonoBehaviour
{
    [Header("可选：场景里已经做好的数字文本")]
    public Text numText;

    [Header("场景里没有体力条时，运行时代码自动搭一条")]
    public bool autoBuild = true;

    [Header("体力条相对 Canvas 右上角的位置（与钻石条对齐）")]
    public Vector2 hudPosition = new Vector2(-108.5f, -96.1f);
    public Vector2 hudSize = new Vector2(164f, 48.8f);

    [Header("在线恢复结算间隔（秒）")]
    public float recoverInterval = 5f;

    [Header("jiliBtn / cebianBtn 贴屏幕左右边缘")]
    public bool anchorEdgeButtons = true;
    public float jiliRightMargin = 16f;
    public float cebianLeftMargin = 14f;

    const string BAR_PATH = "Images/MainUI/energynumber";
    const string PLUS_PATH = "Images/MainUI/btnAddcoin";

    Text txt;
    int lastVersion = -1;
    float nextRecover;

    void Start()
    {
        EnsureUI();
        if (anchorEdgeButtons)
            AnchorEdgeButtons();
        nextRecover = Time.unscaledTime + recoverInterval;
        Refresh(true);
    }

    /// <summary>
    /// 两个角落按钮贴屏幕左右边缘：jiliBtn（领奖）靠右、cebianBtn（侧边栏）靠左。
    /// 场景里已经是边缘锚点了，这里再兜一次——Unity 编辑器不重读磁盘上的场景，
    /// 主界面开着的时候只改 YAML，Play 起来还是旧的中点锚点。
    /// 位置按「缩放后的实际宽度 + 固定边距」算，以后换图、改 LocalScale 都不用再对数字。
    /// </summary>
    void AnchorEdgeButtons()
    {
        AnchorEdge("jiliBtn", 1f, jiliRightMargin, 64f);
        AnchorEdge("cebianBtn", 0f, cebianLeftMargin, 0f);
    }

    /// <summary>side = 0 贴左、1 贴右；y 是相对竖直中心的偏移。</summary>
    static void AnchorEdge(string name, float side, float margin, float y)
    {
        GameObject go = GameObject.Find(name);
        if (go == null)
            return;
        RectTransform rt = go.transform as RectTransform;
        if (rt == null)
            return;

        // 锚点改成同一个点之后，rect.size 就等于 sizeDelta，先取再改
        float visualHalf = rt.rect.size.x * Mathf.Abs(rt.localScale.x) * 0.5f;
        float offset = margin + visualHalf;

        rt.anchorMin = new Vector2(side, 0.5f);
        rt.anchorMax = new Vector2(side, 0.5f);
        rt.pivot = new Vector2(0.5f, 0.5f);
        rt.anchoredPosition = new Vector2(side > 0.5f ? -offset : offset, y);
    }

    void OnEnable()
    {
        // 从关卡/商店回到主界面时立刻刷新，避免显示旧值
        lastVersion = -1;
        Refresh(true);
    }

    void Update()
    {
        if (recoverInterval > 0f && Time.unscaledTime >= nextRecover)
        {
            nextRecover = Time.unscaledTime + recoverInterval;
            ItemController.applyEnergyRecovery();
        }
        Refresh(false);
    }

    void Refresh(bool force)
    {
        if (txt == null)
            return;
        // ItemController.change() 会自增 updateVersion，只有变化时才读写存档
        if (!force && ItemController.updateVersion == lastVersion)
            return;
        lastVersion = ItemController.updateVersion;
        txt.text = ItemController.getNumEnergyItem().ToString();
    }

    // ---------------- 构建 / 复用 ----------------

    void EnsureUI()
    {
        if (numText != null)
        {
            txt = numText;
            return;
        }
        if (!autoBuild)
            return;

        Transform parent = transform.parent != null ? transform.parent : transform;
        Transform found = parent.Find("EnergyInfo");

        if (found != null)
        {
            Transform num = found.Find("Num");
            txt = num != null ? num.GetComponent<Text>() : found.GetComponentInChildren<Text>();
            EnsureButton(found.gameObject);
            MoveJiliButton();
            return;
        }

        BuildBar(parent);
        MoveJiliButton();
    }

    void BuildBar(Transform parent)
    {
        GameObject go = new GameObject("EnergyInfo", typeof(RectTransform));
        go.layer = gameObject.layer;
        go.transform.SetParent(parent, false);

        RectTransform rt = (RectTransform)go.transform;
        rt.anchorMin = new Vector2(1f, 1f);
        rt.anchorMax = new Vector2(1f, 1f);
        rt.pivot = new Vector2(0.5f, 0.5f);
        rt.anchoredPosition = hudPosition;
        rt.sizeDelta = hudSize;

        Image bg = go.AddComponent<Image>();
        Sprite bar = Resources.Load<Sprite>(BAR_PATH);
        if (bar != null)
        {
            bg.sprite = bar;
            bg.preserveAspect = true;
        }
        bg.raycastTarget = true;

        EnsureButton(go);

        // 数字
        GameObject numGo = new GameObject("Num", typeof(RectTransform));
        numGo.layer = gameObject.layer;
        numGo.transform.SetParent(go.transform, false);
        RectTransform nrt = (RectTransform)numGo.transform;
        nrt.anchorMin = new Vector2(0.5f, 0.5f);
        nrt.anchorMax = new Vector2(0.5f, 0.5f);
        nrt.pivot = new Vector2(0.5f, 0.5f);
        nrt.anchoredPosition = new Vector2(5.2f, 0f);
        nrt.sizeDelta = new Vector2(58.4f, 46.6f);

        txt = numGo.AddComponent<Text>();
        txt.font = FindUIFont();
        txt.fontSize = 20;
        txt.color = Color.white;
        txt.alignment = TextAnchor.MiddleCenter;
        txt.horizontalOverflow = HorizontalWrapMode.Overflow;
        txt.verticalOverflow = VerticalWrapMode.Overflow;
        txt.raycastTarget = false;

        Outline outline = numGo.AddComponent<Outline>();
        outline.effectColor = new Color(0f, 0f, 0f, 0.5f);
        outline.effectDistance = new Vector2(1f, -1f);

        // 绿色加号（纯装饰，点击冒泡到父级按钮）
        Sprite plus = Resources.Load<Sprite>(PLUS_PATH);
        if (plus != null)
        {
            GameObject buy = new GameObject("BuyMore", typeof(RectTransform));
            buy.layer = gameObject.layer;
            buy.transform.SetParent(go.transform, false);
            RectTransform brt = (RectTransform)buy.transform;
            brt.anchorMin = new Vector2(1f, 0.5f);
            brt.anchorMax = new Vector2(1f, 0.5f);
            brt.pivot = new Vector2(0.5f, 0.5f);
            brt.anchoredPosition = new Vector2(-21.5f, 0f);
            brt.sizeDelta = new Vector2(60f, 60f);

            Image bi = buy.AddComponent<Image>();
            bi.sprite = plus;
            bi.preserveAspect = true;
            bi.raycastTarget = false;
        }
    }

    /// <summary>没有 Button 就补一个，点了打开商店；场景里已有按钮则不重复绑。</summary>
    void EnsureButton(GameObject go)
    {
        Button btn = go.GetComponent<Button>();
        if (btn != null)
            return;
        btn = go.AddComponent<Button>();
        Image img = go.GetComponent<Image>();
        if (img != null)
            btn.targetGraphic = img;
        btn.onClick.AddListener(delegate { GameStatic.openStorePanel(); });
    }

    /// <summary>领取奖励按钮原来紧贴钻石条，体力条插进来后要往下让位。</summary>
    void MoveJiliButton()
    {
        GameObject jili = GameObject.Find("jiliBtn");
        if (jili == null)
            return;
        RectTransform rt = jili.transform as RectTransform;
        if (rt == null)
            return;
        if (rt.anchoredPosition.y > 70f)
        {
            Vector2 p = rt.anchoredPosition;
            p.y = 64f;
            rt.anchoredPosition = p;
        }
    }

    /// <summary>数字沿用场景里已经用到的中文字体，保持和钻石条一致。</summary>
    static Font FindUIFont()
    {
        Font[] fonts = Resources.FindObjectsOfTypeAll<Font>();
        if (fonts != null)
        {
            for (int i = 0; i < fonts.Length; i++)
            {
                if (fonts[i] != null && fonts[i].name.IndexOf("Droid", System.StringComparison.OrdinalIgnoreCase) >= 0)
                    return fonts[i];
            }
        }
        Font f = Resources.Load<Font>("Font/CarterOne");
        if (f != null)
            return f;
        return Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
    }
}
