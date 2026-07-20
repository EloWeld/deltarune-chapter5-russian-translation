using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

// Экспорт локализуемых спрайтов (те, что в ja-режиме подменялись японскими)
// в sprites/ репозитория: <имя>_<кадр>.png. Их можно перерисовать на русский
// и вшить обратно скриптом import_sprites.csx.
string outDir = "/Users/mtglitch/deltarune-ch5-ru/sprites";
Directory.CreateDirectory(outDir);
string[] names = {
    "spr_bnamekris", "spr_bnameralsei", "spr_bnamesusie", "spr_bnamenoelle",
    "spr_battlemsg", "spr_btact", "spr_btdefend", "spr_btfight", "spr_btitem",
    "spr_btspare", "spr_bttech", "spr_darkmenudesc", "spr_dmenu_captions",
    "spr_quitmessage", "spr_fieldmuslogo", "spr_shop_space_ui",
    "spr_funnytext_dump_her", "spr_funnytext_ass", "spr_face_queen",
    "bg_building_icee_sign_ch5", "spr_dw_fcastle_second_diner_sign_en",
    "spr_cafe_cheese_owe_money", "spr_dw_castle_welcome_sign",
    "spr_dw_fcastle_foyer_sign", "spr_dw_garden_exit",
    "spr_dw_scarecrow_not_enemy_sign", "spr_face_susie_queen",
    "spr_fcastle_jail_chute", "spr_gardenmuslogo", "spr_green_sign",
    "spr_green_sign_owe_money", "spr_green_sign_owe_money_left",
    "spr_green_sign_welcome_pink", "spr_pink_mewers_live",
    "spr_pink_mewers_live_dim", "spr_thrashfit_header", "spr_thrashstats_susie",
};

int files = 0, missing = 0;
using (var tw = new TextureWorker())
{
    foreach (var name in names)
    {
        var s = Data.Sprites.FirstOrDefault(x => x.Name.Content == name);
        if (s == null) { Console.WriteLine($"НЕ НАЙДЕН в Sprites: {name}"); missing++; continue; }
        for (int i = 0; i < s.Textures.Count; i++)
        {
            var t = s.Textures[i]?.Texture;
            if (t == null) continue;
            var img = tw.GetTextureFor(t, name, true);   // с паддингом до полного размера спрайта
            img.Write($"{outDir}/{name}_{i}.png");
            files++;
        }
    }
}
Console.WriteLine($"экспортировано PNG: {files}, не найдено: {missing}");
Console.WriteLine("EXPORT SPRITES DONE");
