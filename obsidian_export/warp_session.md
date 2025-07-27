# Warp Session Recovery - 2025-07-27 20:06

**Database**: `test_data/warp_test.sqlite`
**Time Range**: Last 24 hours
**Extracted**: 2025-07-27T20:06:01.053125

## 📊 Session Stats

- **Commands**: 7
- **Blocks**: 3
- **AI Conversations**: 3
- **Windows**: 1
- **Projects**: 3

## 📋 Recent Commands

### 2025-07-27 19:50:48
**Directory**: `/Users/test/other-project`
**Branch**: `develop`

```bash
git push origin develop
```

Exit code: ✅ 0

### 2025-07-27 19:35:48
**Directory**: `/Users/test/other-project`
**Branch**: `develop`

```bash
ls -la
```

Exit code: ✅ 0

### 2025-07-27 19:20:48
**Directory**: `/Users/test/other-project`
**Branch**: `develop`

```bash
python script.py
```

Exit code: ✅ 0

### 2025-07-27 19:05:48
**Directory**: `/Users/test`
**Branch**: `None`

```bash
cd ../other-project
```

Exit code: ✅ 0

### 2025-07-27 18:45:48
**Directory**: `/Users/test/my-project`
**Branch**: `main`

```bash
git commit -m "fix tests"
```

Exit code: ✅ 0

### 2025-07-27 18:35:48
**Directory**: `/Users/test/my-project`
**Branch**: `main`

```bash
npm test
```

Exit code: ❌ 1

### 2025-07-27 18:05:48
**Directory**: `/Users/test/my-project`
**Branch**: `main`

```bash
git status
```

Exit code: ✅ 0

## 🤖 AI Conversations

### 2025-07-27 19:45:48 - claude-3
**Directory**: `/Users/test/other-project`

**Query**:
> Explain this git push error and how to resolve it

### 2025-07-27 18:55:48 - gpt-4
**Directory**: `/Users/test/other-project`

**Query**:
> Generate a Python script to process CSV files and output summary statistics

### 2025-07-27 18:25:48 - gpt-4
**Directory**: `/Users/test/my-project`

**Query**:
> How do I fix this failing npm test?

## 📁 Project Activity

### [[other-project]]
**Path**: `/Users/test/other-project`
**Commands**: 3
**Branches**: develop
**Success Rate**: 100.0%
**Activity**: 2025-07-27 19:20:48 → 2025-07-27 19:50:48

### [[my-project]]
**Path**: `/Users/test/my-project`
**Commands**: 3
**Branches**: main
**Success Rate**: 66.7%
**Activity**: 2025-07-27 18:05:48 → 2025-07-27 18:45:48

### [[test]]
**Path**: `/Users/test`
**Commands**: 1
**Branches**: None
**Success Rate**: 100.0%
**Activity**: 2025-07-27 19:05:48 → 2025-07-27 19:05:48
