---
title: "正则 ReDoS"
description: "识别带嵌套量词或重叠分支的危险正则，避免灾难性回溯占满 CPU 导致 NGINX 阻塞或拒绝服务。文章说明典型模式与重写思路，帮助你在上线前排除高成本正则。适用于安全审计与上线前自检，帮助团队统一配置规范、减少误配并降低风险。"
---

# 正则表达式可能导致 ReDoS

_Gixy Check ID: `regex_redos`_


某些正则表达式会出现灾难性回溯。攻击者可以构造输入，令正则引擎消耗大量 CPU，导致拒绝服务。

## 不安全示例

```nginx
# 对长串 "a" 发生灾难性回溯
location ~ ^/(a|aa|aaa|aaaa)+$ {
    return 200 "ok";
}
```

像 `/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaab` 这样的路径，可能长时间占用 CPU。

## 更安全的替代方案

- 锚定并简化模式；避免嵌套的“或”与含糊的重复
- 尽量使用线性时间的明确构造
- 在应用昂贵的正则前限制输入长度

```nginx
# 更安全：加锚并简化
location ~ ^/a+$ {
    return 200 "ok";
}
```

## 为什么重要

位置匹配及其他指令中的含糊正则可被远程利用。保持模式简单并加锚，避免已知会触发回溯爆炸的构造。

--8<-- "zh/snippets/nginx-extras-cta.md"
