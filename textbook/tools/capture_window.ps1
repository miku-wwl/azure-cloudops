# Capture the Microsoft Edge window that is showing the given title fragment, at native
# resolution, using PrintWindow(PW_RENDERFULLCONTENT). Writes a PNG of the whole window.
# Usage: pwsh capture_window.ps1 -TitleLike "Control Tower" -Out C:\path\shot.png
param([string]$TitleLike = "", [Parameter(Mandatory=$true)][string]$Out)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class Cap {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr v);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
}
"@
[void][Cap]::SetProcessDpiAwarenessContext([IntPtr]-4)   # per-monitor v2 → physical pixels
$script:hit = [IntPtr]::Zero; $script:title = ""
[Cap]::EnumWindows({ param($h,$l)
  if ([Cap]::IsWindowVisible($h)) {
    $sb = New-Object System.Text.StringBuilder 512; [void][Cap]::GetWindowText($h,$sb,512); $t = $sb.ToString()
    if ($t -like "*Microsoft*Edge*" -and ($TitleLike -eq "" -or $t -like "*$TitleLike*")) { $script:hit = $h; $script:title = $t; return $false }
  }; return $true }, [IntPtr]::Zero) | Out-Null
if ($script:hit -eq [IntPtr]::Zero) { Write-Error "No Edge window matching '$TitleLike'"; exit 2 }
if ([Cap]::IsIconic($script:hit)) { Write-Error "Window is minimized"; exit 3 }
$r = New-Object Cap+RECT; [void][Cap]::GetWindowRect($script:hit, [ref]$r)
$w = $r.R - $r.L; $hgt = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $hgt
$g = [System.Drawing.Graphics]::FromImage($bmp); $hdc = $g.GetHdc()
$ok = [Cap]::PrintWindow($script:hit, $hdc, 2); $g.ReleaseHdc($hdc); $g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
"ok=$ok size=${w}x${hgt} title=$($script:title)"
