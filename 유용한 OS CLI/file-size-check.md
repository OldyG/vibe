# 파일 크기 확인

파일의 바이트 크기를 확인하고, 큰 파일을 찾는 명령어입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 파일 크기 확인

```powershell
Get-ChildItem *.java | Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}} | Format-Table -AutoSize
```

#### 큰 파일 찾기 (100KB 이상)

```powershell
Get-ChildItem -Recurse *.java | Where-Object {$_.Length -gt 100KB} |
    Select-Object Name, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}} |
    Sort-Object "Size(KB)" -Descending
```

---

### macOS / Linux

#### 파일 크기 확인

```bash
ls -lh *.java
```

#### 큰 파일 찾기 (100KB 이상)

```bash
find . -name "*.java" -size +100k -exec ls -lh {} \;
```

---

## 📚 관련 명령어

- [파일 줄 수 확인](./file-line-count.md) - 코드 줄 수로 크기 파악
- [디렉토리 통계](./directory-stats.md) - 디렉토리별 통계
