using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System;

/// <summary>
/// 体力条：显示当前体力数量和距离下一次恢复的倒计时。
/// 真正的体力恢复由 ItemController.applyEnergyRecovery() 结算（按存档里的时间戳），
/// 这里只负责刷新界面和跑倒计时进度，避免多个界面各自加体力导致重复发放。
/// </summary>
public class EnergyBar : MonoBehaviour {
	float totalTime = GameConfig.time_energy_recover;
	float currentTime = 0;
	bool isRun = false;
	Image fillImage;
	public ItemController itemController;
	public Text txtTime;

	void Start () {
		totalTime = GameConfig.time_energy_recover;
		fillImage = GetComponent<Image> ();
		refreshState ();
	}

	/// <summary>体力有变化（消耗/购买/过关奖励）后调用，重新结算并按需启动倒计时。</summary>
	public void checkToStartOffline(){
		refreshState ();
	}

	void refreshState(){
		ItemController.applyEnergyRecovery ();
		updateItem ();
		if (ItemController.getNumEnergyItem () < GameConfig.max_energy_offline) {
			startBar ();
		} else {
			pause ();
			if (txtTime != null)
				txtTime.gameObject.SetActive (false);
		}
		if (itemController != null)
			itemController.updateItemUI ();
	}

	/// <summary>兼容旧调用：结算离线恢复并返回距离下一点体力的剩余秒数。</summary>
	public float updateItemOffline(){
		ItemController.applyEnergyRecovery ();
		if (itemController != null)
			itemController.updateItemUI ();
		return getOfflineTimeOver ();
	}

	float getOfflineTimeOver(){
		long startTime = ItemController.nowSeconds ();
		int lastTime = PlayerPrefs.GetInt (Save.time_energy, (int)Mathf.Min (startTime, 2100000000f));
		long deltaTime = startTime - lastTime;
		if (deltaTime < 0)
			deltaTime = 0;
		long numItem = (long)(deltaTime / GameConfig.time_energy_recover);
		long timeOver = (deltaTime - GameConfig.time_energy_recover * numItem);
		return timeOver;
	}

	Coroutine corUpdateItem;
	public void updateItem(){
		currentTime = getOfflineTimeOver ();
		if (corUpdateItem != null)
			StopCoroutine (corUpdateItem);
	}

	void Update () {
		if (isRun) {
			currentTime += Time.smoothDeltaTime;
			if (fillImage != null)
				fillImage.fillAmount = currentTime / totalTime;
			if (txtTime != null)
				txtTime.text = CommonFunction.getTimeFromSecond ((int)(totalTime - currentTime));
			if(currentTime >= totalTime){
				timeOut();
			}
		}
	}

	public void startBar(){
		isRun = true;
		if(txtTime != null)
			txtTime.gameObject.SetActive (true);
	}

	public void pause(){
		isRun = false;
	}

	public void continueRun(){
		isRun = true;
	}

	public long getTimeRun(){
		return (long) (totalTime - currentTime);
	}

	void timeOut(){
		pause ();
		refreshState ();
	}
}
