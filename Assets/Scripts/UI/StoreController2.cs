using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 商店面板：用钻石（HUD 右上角）购买关卡资源。
/// 提示 / 洗牌改成每关由关卡发放（见 LogicLevel.applyLevelItems），这里默认只卖体力；
/// 需要恢复售卖时把 sellHint / sellRandom 勾上。价格和数量都在 Inspector 里可调。
/// 钻石余额沿用 Save.getPlayerCoin()（这个值就是右上角 RubyInfo 显示的数字）。
/// </summary>
public class StoreController2 : MonoBehaviour
{
    [Header("商品 1：提示")]
    public ItemController.ItemType item1Type = ItemController.ItemType.hint;
    public int item1Amount = 5;
    public int item1Gem = 50;

    [Header("商品 2：洗牌")]
    public ItemController.ItemType item2Type = ItemController.ItemType.random;
    public int item2Amount = 5;
    public int item2Gem = 80;

    [Header("商品 3：体力")]
    public ItemController.ItemType item3Type = ItemController.ItemType.energy;
    public int item3Amount = 10;
    public int item3Gem = 120;

    [Header("界面文本")]
    public Text numItem1;
    public Text numItem2;
    public Text numItem3;
    public Text costItem1;
    public Text costItem2;
    public Text costItem3;

    [Header("是否售卖提示 / 洗牌")]
    [Tooltip("提示和洗牌改成每关由关卡发放（见 LogicLevel.applyLevelItems），再卖就等于白收钻石，默认下架。")]
    public bool sellHint = false;
    public bool sellRandom = false;

    private void Start()
    {
        applyCardPolicy();
        RefreshUI();
    }

    /// <summary>
    /// 下架提示 / 洗牌两张卡；只剩体力一张时把它挪回中间，避免偏在右边。
    /// 卡片根节点从 Inspector 绑定的文本往上找，没绑定时按名字兜底。
    /// </summary>
    private void applyCardPolicy()
    {
        if (sellHint && sellRandom) return;

        GameObject card1 = findCard(numItem1, "Item1");
        GameObject card2 = findCard(numItem2, "Item2");
        GameObject card3 = findCard(numItem3, "Item3");

        if (!sellHint && card1 != null) card1.SetActive(false);
        if (!sellRandom && card2 != null) card2.SetActive(false);

        if (!sellHint && !sellRandom && card3 != null)
        {
            RectTransform rt = card3.GetComponent<RectTransform>();
            if (rt != null) rt.anchoredPosition = new Vector2(0f, rt.anchoredPosition.y);
        }
    }

    private static GameObject findCard(Text label, string cardName)
    {
        Transform t = label != null ? label.transform : null;
        while (t != null)
        {
            if (t.name == cardName) return t.gameObject;
            t = t.parent;
        }
        return GameObject.Find(cardName);
    }

    /// <summary>把配置里的数量/价格写到卡片上。</summary>
    public void RefreshUI()
    {
        SetCard(numItem1, costItem1, item1Amount, item1Gem);
        SetCard(numItem2, costItem2, item2Amount, item2Gem);
        SetCard(numItem3, costItem3, item3Amount, item3Gem);
    }

    private void SetCard(Text amountText, Text costText, int amount, int gemCost)
    {
        if (amountText != null) amountText.text = "x" + amount;
        if (costText != null) costText.text = gemCost.ToString();
    }

    public void onClickItem1()
    {
        Buy(item1Type, item1Amount, item1Gem);
    }

    public void onClickItem2()
    {
        Buy(item2Type, item2Amount, item2Gem);
    }

    public void onClickItem3()
    {
        Buy(item3Type, item3Amount, item3Gem);
    }

    private void Buy(ItemController.ItemType itemType, int amount, int gemCost)
    {
        // 已下架的商品即使被脚本调到这里也不卖
        if (itemType == ItemController.ItemType.hint && !sellHint) return;
        if (itemType == ItemController.ItemType.random && !sellRandom) return;

        int gem = Save.getPlayerCoin();
        if (gem < gemCost)
        {
            ToastManager.showToast(StringUtils.message_not_enough_coin);
            return;
        }

        Save.setPlayerCoin(gem - gemCost);

        switch (itemType)
        {
            case ItemController.ItemType.hint:
                ItemController.addHintItem(amount);
                break;
            case ItemController.ItemType.random:
                ItemController.addRandomItem(amount);
                break;
            case ItemController.ItemType.energy:
                ItemController.addEnergyItem(amount);
                break;
        }

        if (GameStatic.playerInfo != null)
        {
            GameStatic.playerInfo.updatePlayerCoin(Save.getPlayerCoin());
        }

        // 买完体力立刻刷新体力条与恢复倒计时
        if (itemType == ItemController.ItemType.energy && GameStatic.energyBar != null)
        {
            GameStatic.energyBar.checkToStartOffline();
        }

        string itemName = itemType == ItemController.ItemType.hint ? "提示"
                        : itemType == ItemController.ItemType.random ? "洗牌" : "体力";
        ToastManager.showToast("购买成功：" + itemName + " x" + amount);
        Debug.Log($"[商店] 花费 {gemCost} 钻石购买 {itemName} x{amount}，剩余钻石 {Save.getPlayerCoin()}");
    }
}
