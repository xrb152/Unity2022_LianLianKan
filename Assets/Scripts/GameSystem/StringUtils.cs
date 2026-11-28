using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class StringUtils : MonoBehaviour{
	public static string level_lock 	   	= "level_lock";
	public static string number_star_level 	= "number_star_level";
	public static string time_dead         	= "time_dead";
	public static string time_star_1 		= "time_star_1";
	public static string time_star_2 		= "time_star_2";
	public static string time_star_3 		= "time_star_3";
	public static string auto_gen_type		= "auto_gen_type";
	public static string time_gen			= "time_gen";
	public static string time_gen_wait		= "time_gen_wait";
	public static string auto_gen 			= "auto_gen";

	public static string level 				= "level";
	public static string direction 			= "direction";
	public static string constraint 		= "constraint";
	public static string cell1 				= "cell1";
	public static string cell2 				= "cell2";
	public static string row 				= "row";
	public static string col 				= "col";
	public static string stones_fixed 		= "stones_fixed";
	public static string stones_moving 		= "stones_moving";
	public static string frozens_fixed 		= "frozens_fixed";
	public static string pokemon_fixed      = "pokemon_fixed";
	public static string probability 		= "probability";
	public static string number 			= "number";
	public static string hint 				= "hint";
	public static string random 			= "random";
	public static string energy 			= "energy";
	public static string reward 			= "reward"; 
	public static string num_hint 			= "num_hint";
	public static string num_random 		= "num_random";
	public static string type				= "type";
	public static string id 				= "id";
	public static string player_coin        = "player_coin";
	public static string user_item_version  = "user_item_version";
	public static string item_shop_data     = "item_shop_data";
	public static string item_type          = "item_type";
	public static string pack_id 			= "pack_id";
	public static string item_id 			= "item_id";
	public static string description 		= "description";
	public static string cost 				= "cost";
	public static string cost_type 			= "cost_type";
	public static string shop_version		= "shop_version";
	public static string config_version		= "config_version";
	public static string coin_bonus         = "coin_bonus";
	public static string score				= "score";

	//=====Player data==========//
	public static string random_time_1 = "rt_1";
	public static string random_time_2 = "rt_2";
	public static string random_time_3 = "rt_3";
	public static string random_time_4 = "rt_4";
	public static string random_time_5 = "rt_5";
	public static string count_random_time_1 = "crt_1";
	public static string count_random_time_2 = "crt_2";
	public static string count_random_time_3 = "crt_3";
	public static string count_random_time_4 = "crt_4";
	public static string count_random_time_5 = "crt_5";
	public static string random_time_offset_1 = "rto_1";
	public static string random_time_offset_2 = "rto_2";
	public static string random_time_offset_3 = "rto_3";
	public static string random_time_offset_4 = "rto_4";
	public static string random_time_offset_5 = "rto_5";
	public static string has_random_time = "has_random_time";
	public static string rank_global  = "rank_global";
	public static string rank_local   = "rank_local";
	public static string rank_friends = "rank_friends";
	public static string rank_before  = "rank_before";
	public static string rank_after   = "rank_after";
	public static string rate_status  = "rate_status";
	public static string facebook_name = "facebook_name";
	public static string one_signal_player_id = "one_signal_player_id";
	public static string time_buy_remove_ads = "time_buy_remove_ads";
	public static string time_remove_ads = "time_remove_ads";
	public static string remove_ads_pack_id = "remove_ads_pack_id";

	//=====Scene name===========//
	public static string scene_main				= "Main";
	public static string scene_level				= "LevelSence";
	public static string scene_play_off				= "GamePlay";
	public static string scene_online_menu				= "OnlineMenu";
	public static string scene_play_on				= "OnlinePlay";
	public static string scene_play_tutorial				= "Help";

	//=====Leader board==========//
	public static string leader_board_global 	 = "leader_board_global";
	public static string leader_board_by_country = "leader_board_by_country";
	public static string leader_board_by_friends = "leader_board_by_friends";
	public static string list_rank 		= "listRank";
	public static string my_player_rank = "myPlayerRank";
	public static string user_name 		= "userName";
	public static string trophies       = "trophies";
	public static string rank    		= "rank";
	public static string user_id 		= "userId";

	//=====Network Ping Config========//
	public static string network_ping_url   = "network_ping_url";
	public static string network_ping_time  = "network_ping_time";
	public static string network_ping_count = "network_ping_count";

	//=====Push Notification=========//
	public static string time_notify_recover_energy = "time_notify_recover_energy";

	//================= Text trong game================//
	public static string loading = "加载中...";
	public static string loading_old_data = "正在把服务器存档同步到本地...";
	public static string no_facebook_level_data = "还没有好友玩过这一关...";
	public static string loading_online_random_map = "随机地图...";
	public static string loading_online_prepare_map = "初始化地图...";
	public static string not_enough_energy = "体力不足！请等待恢复或前往商店。";
	public static string not_enough_item = "道具不足！";
	public static string time_over = "时间到！";
	public static string can_not_eat_ice = "冰块已经无法再消除了！";
	public static string out_of_game_pause_reason = "中途退出游戏，本局判负，抱歉。";
	public static string out_of_game_enermy_out_reason = "对手已全部离开，你赢了。";
	public static string win_game = "你赢了！";
	public static string lose_game = "你输了！";

	public static string error = "出了点问题，请稍后再试！";
	public static string error_text_empty = "错误！文本不能为空";
	public static string success_store_purchase = "购买成功！你获得了：";
	public static string success = "成功！";
	public static string received_item_from_server = "你获得了：";
	public static string received_coin_from_watching_video = "看视频获得钻石：+";
	public static string received_energy_from_watching_video_click = "你获得了 3 点体力。";
	public static string received_energy_from_facebook_invite = "脸书邀请成功！你获得了：";
	public static string received_energy_from_facebook_login = "脸书登录成功！你获得了：";
	public static string video_skip = "请不要跳过视频。";
	public static string buy = "购买";
	public static string buyed = "已售出";
	public static string active = "激活";
	public static string actived = "已使用";
	public static string update = "更新";
	public static string download_done = "下载完成！";
	public static string downloading = "下载中...";
	public static string not_enough_money = "道具不足，无法购买！请到商店补充。";
	public static string server_connect = "正在连接服务器...";
	public static string lose_trophies = "你输了，失去了 ";
	public static string wait_friend = "等待好友加入...";
	public static string player_out = "对手已离开游戏";
	public static string disconnect = "网络连接已断开。";
	public static string notify_recover_energy = "notify_recover_energy";
	public static string messgae_recover_energy = "体力已恢复，可以继续游戏了...";
	public static string message_not_enough_coin = "钻石不足，无法购买该道具！";
	public static string message_not_enough_ruby = "钻石不足，无法复活！";
	public static string[] message_text_hint = {
		"消掉地图上唯一可消的一对宝可梦，可得 80 分。",
		"当只剩 2 对可消时，消掉其中一对，可得 40 分。",
		"当只剩 3 对可消时，消掉其中一对，可得 20 分。",
		"当可消的对数超过 3 对时，消掉一对，可得 10 分。",
		"连续消掉两对及以上，额外获得 5 分奖励。",
		"赢得在线对战，可以获得免费钻石。",
		"可以在商店用钻石购买道具。",
		"可以在商店用钻石购买提示、洗牌和体力。",
		"活动期间参与游戏，可以获得更多钻石和奖杯。"
	};

	public Text[] tranlateText;
	void Start(){
		foreach(Text text in tranlateText){
			text.text = text.name;
		}
	}

	public static string getNumberDot(double number) {
		return string.Format("{0:#,###0}", number);
	}

	public static string getMessageHint() {
		int length = message_text_hint.Length;
		int count = (int) Random.Range (0, length - 1);
		return message_text_hint [count];
	}
}
