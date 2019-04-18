# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs

# 追加したTimberと他の部材との衝突判定 TODO: ランダムサーチになっているので最適化手法を考える
def collisionDetection(used_timber_list, not_used_timber_list, unused_timber, id_connect):  
    num_used_timber = len(used_timber_list)
    num_not_used_timber = len(not_used_timber_list)
    sum_timber = num_used_timber + num_not_used_timber

    timber1 = unused_timber    # これから生成するTimber
    count = 0                  # timber1と他のused_timberが衝突していない時のカウント
    
    # 衝突判定(unused_timberとused_listのtimber同士の接触判定)
    for i in range(num_used_timber):
        
        # 接合部は衝突とみなさない
        if i == id_connect:
            count = count + 1
        
        # 接合部材以外のused_timberとの衝突判定
        else:
            timber2 = used_timber_list[i]
            curve = rs.IntersectBreps(timber1.surface, timber2.surface)

            # 衝突していない場合
            if curve is None:
                count = count + 1

            # 衝突している場合
            else:
                # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
                # mark_sphere = createMarkSphere(curve)
                # rs.ObjectLayer(mark_sphere, "collision")

                # objectを削除
                rs.DeleteObject(curve[0])
                break


    # 衝突判定(unused_timberとnot_used_listのtimber同士の接触判定)
    for j in range(num_not_used_timber):
        timber2 = not_used_timber_list[j]
        curve = rs.IntersectBreps(timber1.surface, timber2.surface)

        # 衝突していない場合
        if curve is None:
            count = count + 1

        # 衝突している場合
        else:
            # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
            # mark_sphere = createMarkSphere(curve)
            # rs.ObjectLayer(mark_sphere, "collision")

            # objectを削除
            rs.DeleteObject(curve[0])


    # unused_timberがどの部材とも衝突してない場合
    if count == sum_timber:
        return False
    # unused_timberがいずれかの部材と衝突している場合
    else:
        return True

# 追加したTimberと他の部材との衝突判定 TODO: ランダムサーチになっているので最適化手法を考える
def collisionDetectionTolerance(used_timber_list, not_used_timber_list, unused_timber, id_connect, tolerance=250):
    num_used_timber = len(used_timber_list)
    num_not_used_timber = len(not_used_timber_list)
    sum_timber = num_used_timber + num_not_used_timber

    timber1 = unused_timber  # これから生成するTimber
    count = 0  # timber1と他のused_timberが衝突していない時のカウント

    # 衝突判定(unused_timberとused_listのtimber同士の接触判定)
    for i in range(num_used_timber):

        # 接合部は衝突とみなさない
        if i == id_connect:
            count = count + 1

        # 接合部材以外のused_timberとの衝突判定
        else:
            timber2 = used_timber_list[i]
            curve = rs.IntersectBreps(timber1.surface, timber2.surface)

            # 衝突していない場合
            if curve is None:
                count = count + 1

            # 衝突している場合
            else:
                length = 0
                for j in range(len(curve)):
                    length = length + rs.CurveLength(curve[j])

                if length < tolerance:  #  他の材との接触が許容範囲内であるならばOK
                    count = count + 1
                    # print("permitted the intersection : intersection curve length : %s " % (length))
                    #---------------------------------------------------------------------------------------------------
                    # ここに接触時のロボットアームによる切削加工経路生成プログラム、または必要情報生成のプログラムを加える。


                    #---------------------------------------------------------------------------------------------------
                else:
                    for k in range(len(curve)):
                        rs.DeleteObject(curve[k])
                    break

                # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
                # mark_sphere = createMarkSphere(curve)
                # rs.ObjectLayer(mark_sphere, "collision")


    # 衝突判定(unused_timberとnot_used_listのtimber同士の接触判定)
    for j in range(num_not_used_timber):
        timber2 = not_used_timber_list[j]
        curve = rs.IntersectBreps(timber1.surface, timber2.surface)

        # 衝突していない場合
        if curve is None:
            count = count + 1

        # 衝突している場合
        else:
            length = 0
            for j in range(len(curve)):
                length = length + rs.CurveLength(curve[j])

            if length < tolerance:  # 他の材との接触が許容範囲内であるならばOK
                count = count + 1
                # print("permitted the intersection : intersection curve length : %s "%(length) )
                # ---------------------------------------------------------------------------------------------------
                # ここに接触時のロボットアームによる切削加工経路生成プログラム、または必要情報生成のプログラムを加える。

                # ---------------------------------------------------------------------------------------------------
            else:
                for k in range(len(curve)):
                    rs.DeleteObject(curve[k])
                break

            # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
            # mark_sphere = createMarkSphere(curve)
            # rs.ObjectLayer(mark_sphere, "collision")



    # unused_timberがどの部材とも衝突してない場合
    if count == sum_timber:
        return False
    # unused_timberがいずれかの部材と衝突している場合
    else:
        return True

# 追加したTimberと他の部材との衝突判定 TODO: bridge()用の衝突判定を完成させること
def collisionDetection_bridge(used_timber_list, not_used_timber_list, unused_timber, id_connect_1, id_connect_2):
    num_used_timber = len(used_timber_list)
    num_not_used_timber = len(not_used_timber_list)
    sum_timber = num_used_timber + num_not_used_timber

    count = 0
    timber1 = unused_timber

    for i in range(num_used_timber):
        # 接合部は衝突とみなさない
        if i == id_connect_1:
            count = count + 1
        elif i == id_connect_2:
            count = count + 1

        # 接合部材以外のused_timberとの衝突判定
        else:
            timber2 = used_timber_list[i]
            curve = rs.IntersectBreps(timber1.surface, timber2.surface)

            if curve is None:
                count = count + 1
            else:
                # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
                # mark_sphere = createMarkSphere(curve)
                # rs.ObjectLayer(mark_sphere, "collision")

                # objectを削除
                rs.DeleteObject(curve[0])

    for i in range(num_not_used_timber):
        # 接合部材以外のused_timberとの衝突判定

        timber2 = not_used_timber_list[i]
        curve = rs.IntersectBreps(timber1.surface, timber2.surface)

        # 衝突していない場合
        if curve is None:
            count = count + 1

        # 衝突している場合
        else:
            # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
            # mark_sphere = createMarkSphere(curve)
            # rs.ObjectLayer(mark_sphere, "collision")

            # objectを削除
            rs.DeleteObject(curve[0])


    # unused_timberがどの部材とも衝突してない場合
    if count == sum_timber:
        return False

    # unused_timberがいずれかの部材と衝突している場合
    else:
        return True

# 追加したTimberと他の部材との衝突判定 TODO: bridge()用の衝突判定を完成させること
def collisionDetectionTolerance_bridge(used_timber_list, not_used_timber_list, unused_timber, id_connect_1, id_connect_2, tolerance=250):
    num_used_timber = len(used_timber_list)
    num_not_used_timber = len(not_used_timber_list)
    sum_timber = num_used_timber + num_not_used_timber

    count = 0
    timber1 = unused_timber

    for i in range(num_used_timber):
        # 接合部は衝突とみなさない
        if i == id_connect_1:
            count = count + 1
        elif i == id_connect_2:
            count = count + 1

        # 接合部材以外のused_timberとの衝突判定
        else:
            timber2 = used_timber_list[i]
            curve = rs.IntersectBreps(timber1.surface, timber2.surface)

            if curve is None:
                count = count + 1
            else:
                length = 0
                for j in range(len(curve)):
                    length = length + rs.CurveLength(curve[j])

                if length < tolerance:  # 他の材との接触が許容範囲内であるならばOK
                    count = count + 1
                    # print("permitted the intersection : intersection curve length : %s " % (length))
                    # ---------------------------------------------------------------------------------------------------
                    # ここに接触時のロボットアームによる切削加工経路生成プログラム、または必要情報生成のプログラムを加える。

                    # ---------------------------------------------------------------------------------------------------
                else:
                    for k in range(len(curve)):
                        rs.DeleteObject(curve[k])
                    break
                # 衝突部に目印の球体を生成 --> ただの目印なので接触処理するときはコメントアウトしてもらえればと
                # mark_sphere = createMarkSphere(curve)
                # rs.ObjectLayer(mark_sphere, "collision")

    for i in range(num_not_used_timber):
        # 接合部材以外のused_timberとの衝突判定

        timber2 = not_used_timber_list[i]
        curve = rs.IntersectBreps(timber1.surface, timber2.surface)

        # 衝突していない場合
        if curve is None:
            count = count + 1

        # 衝突している場合

        else:
            length = 0
            for j in range(len(curve)):
                length = length + rs.CurveLength(curve[j])

            if length < tolerance:  # 他の材との接触が許容範囲内であるならばOK
                count = count + 1
                # print("permitted the intersection : intersection curve length : %s " % (length))
                # ---------------------------------------------------------------------------------------------------
                # ここに接触時のロボットアームによる切削加工経路生成プログラム、または必要情報生成のプログラムを加える。

                # ---------------------------------------------------------------------------------------------------
            else:
                for k in range(len(curve)):
                    rs.DeleteObject(curve[k])
                break

    # unused_timberがどの部材とも衝突してない場合
    if count == sum_timber:
        return False

    # unused_timberがいずれかの部材と衝突している場合
    else:
        return True



# 衝突した場所に目印(球体)を生成
def createMarkSphere(curve_list):

    curve = curve_list[0]

    domain = rs.CurveDomain(curve)
    t = domain[1] / 2.0
    point = rs.EvaluateCurve(curve, t)

    mark_collision = rs.AddSphere(point, 40)
    rs.ObjectColor(mark_collision, [255, 0, 0])

    return mark_collision



# モジュールテスト
if __name__ == "__main__":
    print("Module Test")








