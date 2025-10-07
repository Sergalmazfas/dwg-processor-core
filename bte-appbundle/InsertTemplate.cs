/*
 * BTE Template Insert Plugin for AutoCAD Design Automation
 * Based on official Autodesk APS AppBundle format
 * References: https://aps.autodesk.com/en/docs/design-automation/v3/
 */

using System;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;

[assembly: CommandClass(typeof(BTEPlugin.InsertTemplate))]

namespace BTEPlugin
{
    public class InsertTemplate : IExtensionApplication
    {
        public void Initialize()
        {
            // Called when AppBundle is loaded
            Application.DocumentManager.MdiActiveDocument?.Editor.WriteMessage(
                "\n🔧 BTE Insert Template Plugin loaded\n"
            );
        }

        public void Terminate()
        {
            // Called when AppBundle is unloaded
        }

        [CommandMethod("INSERTBTE")]
        public void InsertBTETemplate()
        {
            Document doc = Application.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                Console.WriteLine("❌ No active document");
                return;
            }

            Database db = doc.Database;
            Editor ed = doc.Editor;

            try
            {
                ed.WriteMessage("\n🔸 Starting BTE template insertion...\n");

                using (Transaction tr = db.TransactionManager.StartTransaction())
                {
                    BlockTable bt = tr.GetObject(db.BlockTableId, OpenMode.ForWrite) as BlockTable;

                    // Вставка шаблона (упрощенная версия для теста)
                    // В production здесь будет реальная логика вставки BTE блоков
                    
                    ed.WriteMessage("🔸 Processing DWG with BTE logic...\n");

                    // Для теста просто сохраняем файл
                    // TODO: Добавить реальную логику вставки BTE шаблона
                    
                    tr.Commit();
                    ed.WriteMessage("✅ BTE template processing complete\n");
                }

                // Сохраняем результат
                db.SaveAs("output.dwg", DwgVersion.Current);
                ed.WriteMessage("✅ File saved as output.dwg\n");
            }
            catch (Exception ex)
            {
                ed.WriteMessage($"❌ Error: {ex.Message}\n");
                throw;
            }
        }
    }
}

