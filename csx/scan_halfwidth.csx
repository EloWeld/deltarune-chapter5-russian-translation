using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

// ищем все code-entry, где встречается константа 65377 (маркер проверки полуширинных символов)
foreach (var code in Data.Code)
{
    if (code == null || code.ParentEntry != null) continue;
    bool hit = false;
    foreach (var instr in code.Instructions)
    {
        try
        {
            if (instr.ValueInt == 65377 || instr.ValueInt == 65376) { hit = true; break; }
        }
        catch { }
    }
    if (hit) Console.WriteLine(code.Name.Content);
}
Console.WriteLine("SCAN DONE");
