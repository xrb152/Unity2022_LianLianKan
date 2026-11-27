using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 牌面主题清单，对应 Resources/TileThemes/themes.json。
/// 新增主题只需建目录 + 在 json 里加一条，无需改代码。
/// </summary>
[System.Serializable]
public class TileThemeEntry
{
    public string id;
    public string name;
}

[System.Serializable]
public class TileThemeManifest
{
    public string defaultTheme;
    public TileThemeEntry[] themes;
}

/// <summary>
/// 牌面主题管理：把「牌面用哪套图」从场景引用里解耦出来。
///
/// 目录约定：
///   Assets/Resources/TileThemes/themes.json      主题清单
///   Assets/Resources/TileThemes/shanhai/0.png    … 35.png（文件名即牌面 id）
///
/// 运行时用 Resources.LoadAll 读整个目录，按文件名建索引；
/// 取图时先按原名找，找不到再尝试去掉尾部的皮肤字母（a/b/d），
/// 所以同一套图可以同时服务经典/可爱/新版三种皮肤而不必备三份。
/// 主题没有覆盖到的图（如 stone3d、Crate、IceBox）会自动回落到场景里的原列表。
/// </summary>
public static class TileThemeManager
{
    public const string PrefsKey = "tile_theme_id";
    public const string ThemeRoot = "TileThemes/";
    public const string ManifestPath = "TileThemes/themes";

    static bool loaded;
    static string activeId = "";
    static TileThemeManifest manifest;
    static Dictionary<string, Sprite> sprites;

    /// <summary>当前生效的主题 id，空字符串表示不使用主题。</summary>
    public static string ActiveId
    {
        get { EnsureLoaded(); return activeId; }
    }

    /// <summary>当前主题是否真的有可用图片。</summary>
    public static bool HasTheme
    {
        get { EnsureLoaded(); return sprites != null && sprites.Count > 0; }
    }

    /// <summary>主题清单，可能为 null。</summary>
    public static TileThemeManifest Manifest
    {
        get { EnsureLoaded(); return manifest; }
    }

    static void EnsureLoaded()
    {
        if (loaded)
            return;
        loaded = true;

        TextAsset json = Resources.Load<TextAsset>(ManifestPath);
        if (json != null)
        {
            try
            {
                manifest = JsonUtility.FromJson<TileThemeManifest>(json.text);
            }
            catch (System.Exception e)
            {
                Debug.LogWarning("[TileTheme] themes.json 解析失败：" + e.Message);
                manifest = null;
            }
        }

        activeId = PlayerPrefs.GetString(PrefsKey, "");
        if (string.IsNullOrEmpty(activeId) && manifest != null && !string.IsNullOrEmpty(manifest.defaultTheme))
            activeId = manifest.defaultTheme;

        LoadSprites();
    }

    static void LoadSprites()
    {
        sprites = new Dictionary<string, Sprite>();
        if (string.IsNullOrEmpty(activeId))
            return;

        Sprite[] arr = Resources.LoadAll<Sprite>(ThemeRoot + activeId);
        if (arr == null)
            return;

        for (int i = 0; i < arr.Length; i++)
        {
            Sprite s = arr[i];
            if (s == null)
                continue;
            string key = s.name.ToLower();
            if (!sprites.ContainsKey(key))
                sprites.Add(key, s);
        }
    }

    /// <summary>
    /// 按牌面 id 取图，取不到返回 null（调用方应回落到原有列表）。
    /// key 形如 "3"、"3a"、"3b"、"3d"。
    /// </summary>
    public static Sprite GetSprite(string key)
    {
        EnsureLoaded();
        if (sprites == null || sprites.Count == 0 || string.IsNullOrEmpty(key))
            return null;

        key = key.ToLower();

        Sprite found;
        if (sprites.TryGetValue(key, out found))
            return found;

        if (key.Length > 1)
        {
            char tail = key[key.Length - 1];
            if (tail == 'a' || tail == 'b' || tail == 'd')
            {
                if (sprites.TryGetValue(key.Substring(0, key.Length - 1), out found))
                    return found;
            }
        }
        return null;
    }

    /// <summary>切换主题并立即生效（下次取图时用新目录）。</summary>
    public static void SetTheme(string id)
    {
        PlayerPrefs.SetString(PrefsKey, id == null ? "" : id);
        PlayerPrefs.Save();
        activeId = id == null ? "" : id;
        loaded = true;
        LoadSprites();
    }

    /// <summary>清掉用户选择，回到 themes.json 里的 defaultTheme。</summary>
    public static void ResetToDefault()
    {
        PlayerPrefs.DeleteKey(PrefsKey);
        PlayerPrefs.Save();
        loaded = false;
        EnsureLoaded();
    }
}
