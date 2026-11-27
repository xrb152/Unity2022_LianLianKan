using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// HUD 上的「免费金币」按钮：点击弹出广告确认框，看完抖音激励视频发放道具。
/// 原文件依赖外部 HyperWe.CurrencyInjector 注入框架（本工程没有这套框架，会导致编译失败），
/// 这里改为直接调用本工程已有的 ItemController 读写道具，外部行为保持不变。
/// </summary>
[RequireComponent(typeof(Button))]
public class FreeCoinButton : MonoBehaviour
{
    [SerializeField]
    private ItemController.ItemType rewardItemType = ItemController.ItemType.hint;

    [SerializeField]
    private int rewardAmount = 1;

    private Button button;

    private void Start()
    {
        button = GetComponent<Button>();
        if (button != null)
        {
            button.onClick.AddListener(OnClick);
        }
    }

    private void OnDestroy()
    {
        if (button != null)
        {
            button.onClick.RemoveListener(OnClick);
        }
    }

    public void OnClick()
    {
        Debug.Log("[广告] 点击免费金币按钮，弹出激励视频确认框");
        AdConfirm.Show(GrantReward);
    }

    private void GrantReward()
    {
        switch (rewardItemType)
        {
            case ItemController.ItemType.hint:
                ItemController.addHintItem(rewardAmount);
                break;
            case ItemController.ItemType.random:
                ItemController.addRandomItem(rewardAmount);
                break;
            case ItemController.ItemType.energy:
                ItemController.addEnergyItem(rewardAmount);
                break;
        }

        Debug.Log($"[广告] 激励视频完成，发放道具 {rewardItemType} x{rewardAmount}");
    }
}
