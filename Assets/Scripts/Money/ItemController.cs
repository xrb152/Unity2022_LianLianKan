using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System;
using UnityEngine.Events;

public class ItemController : MonoBehaviour {
	public enum ItemType {hint,random,energy};
	public ItemType itemType;
	public static string item_key {
		get{
			if (GameStatic.currentMode == Const.GAME_MODE_EVENT) {
				return "num_item_type_event_";
			} else {
				return "num_item_type_";
			}
		}
		set{
			item_key = value;
		}
	}
	[Serializable]
	public class EventUseEnergy : UnityEvent { }

	public static int updateVersion = 0;
	public int _updateVersion = 0;

	public EventUseEnergy OnEventUseEnergy;
	void Start () {
		updateItemUI ();
	}

	public static int getNumHintItem(){
		if (!PlayerPrefs.HasKey (item_key + ItemType.hint.GetHashCode ())) {
			PlayerPrefs.SetInt (item_key + ItemType.hint.GetHashCode (), GameConfig.num_item_hint_start);
			PlayerPrefs.Save ();
			change ();
		}
		return PlayerPrefs.GetInt (item_key + ItemType.hint.GetHashCode());
	}

	public static int getNumRandomItem(){
//		PlayerPrefs.SetInt (item_key + ItemType.random.GetHashCode (),1);
		if (!PlayerPrefs.HasKey (item_key + ItemType.random.GetHashCode ())) {
			PlayerPrefs.SetInt (item_key + ItemType.random.GetHashCode (), GameConfig.num_item_random_start);
			PlayerPrefs.Save ();
			change ();
		}
		return PlayerPrefs.GetInt (item_key + ItemType.random.GetHashCode());
	}

	public static int getNumEnergyItem(){
		if (!PlayerPrefs.HasKey (item_key + ItemType.energy.GetHashCode ())) {
			PlayerPrefs.SetInt (item_key + ItemType.energy.GetHashCode (), GameConfig.num_item_energy_start);
			PlayerPrefs.Save ();
			change ();
		}
		int num = PlayerPrefs.GetInt (item_key + ItemType.energy.GetHashCode ());
		return num > 0 ? num : 0 ;
	}

	public static void setHintItem(int number){
		GameStatic.currentHint = number;
		PlayerPrefs.SetInt (item_key + ItemType.hint.GetHashCode (), number);
		PlayerPrefs.Save ();
		change ();
	}

	public static void addHintItem(int number) {
		PlayerPrefs.SetInt (item_key + ItemType.hint.GetHashCode (), getNumHintItem() + number);
		PlayerPrefs.Save ();
		change ();
	}

	public static void setEnergyItem(int number){
		if (number < 0)
			number = 0;
		PlayerPrefs.SetInt (item_key + ItemType.energy.GetHashCode (), number);
		PlayerPrefs.Save ();
		change ();
	}

	public static bool addEnergyItem(){
		int num = getNumEnergyItem ();
		if (num < GameConfig.max_energy_offline) {
			PlayerPrefs.SetInt (item_key + ItemType.energy.GetHashCode (), num+1);
			PlayerPrefs.Save ();
			return true;
		}
		return false;
	}

	public static void addEnergyItem(int number){
		PlayerPrefs.SetInt (item_key + ItemType.energy.GetHashCode (), getNumEnergyItem() + number);
		PlayerPrefs.Save ();
		change ();
	}

	public bool useHintItem(){
		if (getNumHintItem () <= 0) {
			ToastManager.showToast (StringUtils.not_enough_item);
			return false;
		}
		setHintItem (getNumHintItem () - 1);
		return true;
	}

	public bool useRandomItem(){
		if (getNumRandomItem () <= 0) {
			ToastManager.showToast (StringUtils.not_enough_item);
			return false;
		}
		setRandomItem (getNumRandomItem () - 1);
		return true;
	}

	public bool useEnergyItem(){
		if(OnEventUseEnergy != null) OnEventUseEnergy.Invoke ();
		return USEEnergyItem ();
	}

	/// <summary>当前 UTC 秒数（体力恢复用）。</summary>
	public static long nowSeconds(){
		return (long)(DateTime.UtcNow.Subtract (new DateTime (1970, 1, 1))).TotalSeconds;
	}

	/// <summary>
	/// 按离线时间恢复体力：每 GameConfig.time_energy_recover 秒恢复 1 点，上限 GameConfig.max_energy_offline。
	/// 结果直接写回存档，返回本次恢复的点数。可以重复调用（进主界面/战斗/切回前台时各调一次）。
	/// </summary>
	public static int applyEnergyRecovery(){
		int max = Mathf.Max (1, GameConfig.max_energy_offline);
		int cur = getNumEnergyItem ();
		int now = (int)Mathf.Min (nowSeconds (), 2100000000f);

		if (!PlayerPrefs.HasKey (Save.time_energy)) {
			writeEnergyStamp (now);
			return 0;
		}

		int last = PlayerPrefs.GetInt (Save.time_energy, 0);
		if (last <= 0 || last > now) {
			// 存档时间异常（改表/时区跳动），重新计时
			writeEnergyStamp (now);
			return 0;
		}

		if (cur >= max) {
			// 满体力时不累积进度；每隔一分钟才落盘一次，避免频繁写磁盘
			if (now - last > 60)
				writeEnergyStamp (now);
			return 0;
		}

		int step = Mathf.Max (1, GameConfig.time_energy_recover);
		long delta = now - last;
		int gained = (int)(delta / step);
		if (gained <= 0)
			return 0;

		int newNum = Mathf.Min (max, cur + gained);
		long used = (long)(newNum - cur) * step;
		long stamp = newNum >= max ? now : last + used;

		setEnergyItem (newNum);                    // 内部会 change()，界面自动刷新
		writeEnergyStamp ((int)stamp);
		return newNum - cur;
	}

	/// <summary>体力恢复时间戳用 int 存（float 只有 7 位有效数字，存 Unix 秒会丢精度）。</summary>
	static void writeEnergyStamp(int seconds){
		PlayerPrefs.SetInt (Save.time_energy, seconds);
		PlayerPrefs.Save ();
	}

	/// <summary>开始新一局时扣体力，返回 false 表示体力不足（已经弹过提示）。</summary>
	public static bool useEnergyToStartRun(){
		int cost = GameConfig.num_energy_cost_per_run;
		if (cost <= 0)
			return true;

		int cur = getNumEnergyItem ();
		if (cur < cost) {
			ToastManager.showToast (StringUtils.not_enough_energy);
			return false;
		}

		// 从满体力开始消耗时，恢复计时从这一刻重新算
		if (cur >= GameConfig.max_energy_offline)
			writeEnergyStamp ((int)Mathf.Min (nowSeconds (), 2100000000f));

		setEnergyItem (cur - cost);
		if (GameStatic.energyBar != null)
			GameStatic.energyBar.checkToStartOffline ();
		return true;
	}

	public static bool USEEnergyItem(){
		int num = getNumEnergyItem ();
		if (num <= 0) {
			ToastManager.showToast (StringUtils.not_enough_energy);
			return false;
		}
		updateTimeEnergy = true;

		Save.setEnergyItem (num- 1);
		if(GameStatic.energyBar!= null)
			GameStatic.energyBar.checkToStartOffline ();
		return true;
	}

	//void updateItemEnergyOnline(){
	//	GSRequestData data = new GSRequestData();
	//	data.Add ("get_server_time", true);
	//	GSM.sendUserRequest (data, res => {
	//		if(res == null){
	//			PlayerPrefs.SetInt (Save.time_energy,(int) (DateTime.UtcNow.Subtract(new DateTime(1970, 1, 1))).TotalSeconds);
	//			return;
	//		}

	//		int startTime =(int) res.GetLong("data")/1000;
	//		PlayerPrefs.SetInt (Save.time_energy_server, startTime);
	//		startTime =(int) (DateTime.UtcNow.Subtract(new DateTime(1970, 1, 1))).TotalSeconds;
	//		PlayerPrefs.SetInt (Save.time_energy, startTime);
	//		PlayerPrefs.Save ();
	//	});
	//}

	public static void setRandomItem(int number){
		GameStatic.currentRandom = number;
		PlayerPrefs.SetInt (item_key + ItemType.random.GetHashCode (), number);
		PlayerPrefs.Save ();
		change ();
	}

	public static void addRandomItem (int number) {
		PlayerPrefs.SetInt (item_key + ItemType.random.GetHashCode (),getNumRandomItem() + number);
		PlayerPrefs.Save ();
		change ();
	}



	public void updateItemUI(){
		if (itemType == ItemType.hint) {
			GetComponent<Text> ().text = getNumHintItem () + "";
		}
		if (itemType == ItemType.random) {
			GetComponent<Text> ().text = getNumRandomItem() + "";
		}
		if (itemType == ItemType.energy) {
			GetComponent<Text> ().text = getNumEnergyItem() + "";
		}
	}

	static bool updateTimeEnergy = false;
	void Update(){
        if (_updateVersion < updateVersion)
        {
            updateItemUI();
            _updateVersion = updateVersion;
            //if (GSM.user != null)
            //{
            //    if (itemType == ItemType.hint)
            //    {
            //        GSM.user.AddNumber(GSM.hint, getNumHintItem());
            //        Save.saveUser(GSM.user);
            //    }
            //    if (itemType == ItemType.random)
            //    {
            //        GSM.user.AddNumber(GSM.hint, getNumRandomItem());
            //        Save.saveUser(GSM.user);
            //    }
            //    if (itemType == ItemType.energy)
            //    {
            //        GSM.user.AddNumber(GSM.hint, getNumEnergyItem());
            //        Save.saveUser(GSM.user);
            //    }
            //}
        }
        //if (updateTimeEnergy && GS.Authenticated)
        //{
        //    updateTimeEnergy = false;
        //    updateItemEnergyOnline();
        //}
    }

	public static void change(){
		updateVersion++;
	}
}
