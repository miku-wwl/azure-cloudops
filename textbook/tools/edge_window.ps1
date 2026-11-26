# Keep the Edge window renderable for Console captures without stealing the user's focus.
# -Mode bottom : restore (no activation) and place behind other windows
# -Mode state  : just report state
param([ValidateSet("bottom","top","state")][string]$Mode = "state")
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class EW {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint f);
}
"@
$script:all = New-Object System.Collections.ArrayList
[EW]::EnumWindows({ param($w,$l) if ([EW]::IsWindowVisible($w)) { $sb = New-Object System.Text.StringBuilder 512; [void][EW]::GetWindowText($w,$sb,512); if ($sb.ToString() -like "*Microsoft*Edge*") { [void]$script:all.Add(@($w, $sb.ToString())) } }; return $true }, [IntPtr]::Zero) | Out-Null
if ($script:all.Count -eq 0) { "no-edge-window"; exit 1 }
foreach ($pair in $script:all) {
  $h = $pair[0]
  if ($Mode -ne "state" -and [EW]::IsIconic($h)) { [void][EW]::ShowWindow($h, 4) }   # SW_SHOWNOACTIVATE：恢复但不抢焦点
  if ($Mode -eq "bottom") { [void][EW]::SetWindowPos($h, [IntPtr]1, 0, 0, 0, 0, 0x0013) }  # HWND_BOTTOM
  $t = $pair[1]; if ($t.Length -gt 60) { $t = $t.Substring(0, 60) }
  "hwnd=$h iconic=$([EW]::IsIconic($h)) title=$t"
}
