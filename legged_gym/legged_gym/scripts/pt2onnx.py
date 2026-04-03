import torch
import torch.nn as nn
import os

# ==========================================
# 1. 定义一个 Wrapper，只保留 Actor 网络
# ==========================================
# 强化学习框架通常保存的是 ActorCritic 整体模型
# 真机部署时我们只需要 Actor。使用 Wrapper 可以干净地剥离它。
class ActorDeploymentWrapper(nn.Module):
    def __init__(self, actor_critic_model):
        super().__init__()
        # 假设你的 actor 网络在原模型中叫 .actor
        # 如果你使用的是原版 rsl_rl，提取它的 actor 层
        self.actor = actor_critic_model.actor 
        
    def forward(self, obs):
        # 纯前向传播，不包含任何梯度的计算和分布采样
        return self.actor(obs)

def export_policy_to_onnx(model_path, onnx_save_path, num_obs):
    print(f"[*] 开始加载 PyTorch 模型: {model_path}")
    
    # ==========================================
    # 2. 实例化你的网络并加载权重
    # ==========================================
    # 这里请替换为你实际初始化 ActorCritic 的代码
    # 比如: ac_model = ActorCritic(num_obs=num_obs, num_actions=12, ...)
    # 伪代码演示：
    # ac_model = YourActorCriticClass(...) 
    # checkpoint = torch.load(model_path, map_location='cpu')
    # ac_model.load_state_dict(checkpoint['model_state_dict'])
    
    # 将模型包装，只暴露 Actor
    deployment_policy = ActorDeploymentWrapper(ac_model)
    
    # ⚠️ 极其重要：必须切换到评估模式！
    # 否则 BatchNorm/Dropout 等层的行为在推理时会出错
    deployment_policy.eval()
    deployment_policy.to('cpu') # 导出时通常放在 CPU 上进行

    # ==========================================
    # 3. 创建 Dummy Input (虚拟输入)
    # ==========================================
    # 形状通常为 [batch_size, num_obs]。真机上通常只控制 1 台狗，所以 batch_size=1
    dummy_input = torch.randn(1, num_obs, dtype=torch.float32, device='cpu')

    # ==========================================
    # 4. 执行 ONNX 导出
    # ==========================================
    print(f"[*] 正在导出 ONNX 模型至: {onnx_save_path}")
    torch.onnx.export(
        deployment_policy,             # 准备导出的纯 Actor 模型
        dummy_input,                   # 对应尺寸的虚拟输入
        onnx_save_path,                # 导出的文件路径
        export_params=True,            # 将训练好的权重参数存储在 ONNX 文件内
        opset_version=14,              # Opset 版本，11 或 14 兼容性最好
        do_constant_folding=True,      # 执行常量折叠优化 (提升 C++ 推理速度)
        input_names=['obs'],           # 设定输入节点的名称，C++ 里会用到
        output_names=['actions'],      # 设定输出节点的名称，C++ 里会用到
        
        # 可选：如果你的 batch_size 可能发生变化，可以开启动态轴
        # 如果真机固定只跑一个控制循环，这里可以直接注释掉以获得极致优化
        # dynamic_axes={
        #     'obs': {0: 'batch_size'},  
        #     'actions': {0: 'batch_size'}
        # }
    )
    print("[+] ONNX 模型导出成功！")

# ==========================================
# 5. 验证导出的模型 (强烈建议)
# ==========================================
def verify_onnx(onnx_path):
    try:
        import onnx
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        print("[+] ONNX 模型结构验证通过，没有发现错误！")
    except ImportError:
        print("[-] 未安装 onnx 库，跳过验证。建议通过 pip install onnx 安装。")
    except Exception as e:
        print(f"[-] 验证失败: {e}")

if __name__ == '__main__':
    # 配置你的路径和参数
    PT_MODEL_PATH = "/root/gpufree-data/HIMLoco/legged_gym/logs/rough_m2/Apr02_19-31-28_/model_2040.pt"
    ONNX_SAVE_PATH = "/root/gpufree-data/HIMLoco/legged_gym/logs/rough_m2/exported/policies/m2_him.onnx"
    NUM_OBS = 270 # 必须与你训练时的 obs 维度完全一致
    
    export_policy_to_onnx(PT_MODEL_PATH, ONNX_SAVE_PATH, NUM_OBS)
    verify_onnx(ONNX_SAVE_PATH)
    pass