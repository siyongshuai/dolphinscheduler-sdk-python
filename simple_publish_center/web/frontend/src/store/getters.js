const getters = {
  // 用户相关
  token: state => state.user.token,
  userInfo: state => state.user.userInfo,
  userId: state => state.user.userInfo?.userId,
  username: state => state.user.userInfo?.username,
  role: state => state.user.userInfo?.role,
  
  // 工作流相关
  workflows: state => state.workflow.list,
  workflowTotal: state => state.workflow.total,
  currentWorkflow: state => state.workflow.current,
  
  // 脚本相关
  scripts: state => state.script.list,
  scriptTotal: state => state.script.total,
  
  // 执行实例相关
  instances: state => state.instance.list,
  instanceTotal: state => state.instance.total,
  currentInstance: state => state.instance.current
}

export default getters 