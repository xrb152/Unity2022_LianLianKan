using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 商店面板：用钻石（HUD 右上角）购买账号道具。
/// 三张卡分别对应 提示 / 洗牌 / 体力，价格和数量都在 Inspector 里可调。
/// 道具是账号资源（PlayerPrefs），买了永久累积、开局不重置，所以提示和洗牌都可以卖。
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

    private void Start()
    {
        RefreshUI();
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
