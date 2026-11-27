using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// HUD 上的「免费金币」按钮（场景节点 jiliBtn）。
/// 点击弹出 AdConfirm 激励视频确认框，看完抖音激励视频后发放奖励。
/// 默认发放 100 金币，与 AdConfirm 弹窗里显示的「添加金币 100」一致。
/// 之前 jiliBtn 的 Button 是直接 SetActive(AdConfirm)，没有设置 onCompleted 回调，
/// 所以广告看完也不会发任何东西；这里改为走 AdConfirm.Show(callback)。
/// </summary>
[RequireComponent(typeof(Button))]
public class JiliRewardButton : MonoBehaviour
{
    public enum RewardType
    {
        [InspectorName("金币")]
        Coin,
        [InspectorName("道具")]
        Item
    }

    [Header("奖励类型")]
    [SerializeField] private RewardType rewardType = RewardType.Coin;

    [Header("金币奖励（rewardType = Coin 时生效）")]
    [SerializeField] private int rewardCoin = 100;

    [Header("道具奖励（rewardType = Item 时生效）")]
    [SerializeField] private ItemController.ItemType rewardItemType = ItemController.ItemType.hint;
    [SerializeField] private int rewardItemAmount = 1;

    private Button button;

    private void Awake()
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
        if (rewardType == RewardType.Coin)
        {
            Save.addPlayerCoin(rewardCoin);
            if (GameStatic.playerInfo != null)
            {
                GameStatic.playerInfo.updatePlayerCoin(Save.getPlayerCoin());
            }

            ToastManager.showToast(StringUtils.received_coin_from_watching_video + rewardCoin);
            Debug.Log($"[广告] 激励视频完成，发放金币 x{rewardCoin}，当前金币 {Save.getPlayerCoin()}");
        }
        else
        {
            switch (rewardItemType)
            {
                case ItemController.ItemType.hint:
                    ItemController.addHintItem(rewardItemAmount);
                    break;
                case ItemController.ItemType.random:
                    ItemController.addRandomItem(rewardItemAmount);
                    break;
                case ItemController.ItemType.energy:
                    ItemController.addEnergyItem(rewardItemAmount);
                    break;
            }

            Debug.Log($"[广告] 激励视频完成，发放道具 {rewardItemType} x{rewardItemAmount}");
        }
    }
}
