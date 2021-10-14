#/***********************************************************************
# * Licensed Materials - Property of IBM
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2021
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp.
# ************************************************************************/
__author__ = "SPSS, DPN"
__version__ = "1.1.2"

import tempfile, spss, spssaux, random
from extension import Template, Syntax, checkrequiredparams, processcmd
from spssaux import _smartquote
from spss import CellText

def Run(args):
    """Execute the STATS FLEISS KAPPA command"""

    args = args[list(args.keys())[0]]

    oobj = Syntax([
        Template("VARIABLES", subc="",  ktype="existingvarlist", var="variables", islist=True),
        Template("CILEVEL", subc="OPTIONS",  ktype="float", var="cilevel"),
        Template("HELP", subc="", ktype="bool")])

    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg
    if "HELP" in args:
        helper()
    else:
        processcmd(oobj, args, fleisskappaextension)

def helper():
    """Open html help in default browser window.

    The location is computed from the current module name."""

    import webbrowser, os.path

    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "STATS_FLEISS_KAPPA_SYNTAX_HELP.htm"

    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print((_("Help file not found:") + helpspec))
try:    
    from extension import helper
except:
    pass

# Add expandvarnames in order to be able to handle TO or ALL specifications

def expandvarnames(varnames):
    """Return varnames with ALL and TO expansion"""
    
    # varnames allows the construct v1, v2, ... ALL to coerce the order
    # as well as TO and ALL expansion
    vardict = None
    varnamesLower = [item.lower() for item in varnames]
    try:
        # check for and process ALL name
        allLoc = varnamesLower.index('all')
    except ValueError:
        allvars = []
    else:
        vardict = spssaux.VariableDict()
        if allLoc != len(varnames) -1:
            raise ValueError(_("""ALL must be the last item in the variable list"""))
        allvars = vardict.expand("ALL")
        varnames = varnames[:-1]

    # process TO
    if 'to' in varnamesLower:
        if not vardict:
            vardict = spssaux.VariableDict()
        varnames = vardict.expand(varnames)
    # append ALL result if it was specified
    # would use set union but order matters
    for item in allvars:
        if not (item in varnames or item.lower() in varnames):
            varnames.append(item)
    return varnames

def GetWeightSum(varlist=None):
    """Return the sum of the case weights as calculated by DESCRIPTIVES
    
    varlist is an optional variable list that would cause cases to be listwise deleted
    If weights are not on, the return value is the unweighted number of cases."""
    
    if varlist is None:
        varlist = [spss.GetWeightVar()]
    if not varlist:
        varlist = ["V" + str(random.random(.1,1))]
        spss.Submit("""TEMPORARY.
COMPUTE %s = 0.""" % varlist[0])
    tag, err = spssaux.CreateXMLOutput("DESCRIPTIVES %s /STATISTICS=MIN." % " ".join(varlist),
        omsid='Descriptives')
        #subtype='Descriptive Statistics')
    stats = spss.EvaluateXPath(tag, "/", 
        """//pivotTable[@subType="Descriptive Statistics"]//dimension/category[last()]/*//cell/@number""")
    spss.DeleteXPathHandle(tag)
    return float(stats[-1])

def fleisskappaextension(variables, cilevel=95):
    
    varnames = expandvarnames(variables)
    vardict = spssaux.VariableDict(varnames)
    if len(vardict) != len(varnames):
        spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
        table = spss.BasePivotTable("Warnings ","Warnings")
        table.Append(spss.Dimension.Place.row,"rowdim",hideLabels=True)
        rowLabel = CellText.String("1")
        table[(rowLabel,)] = CellText.String(_("""An invalid variable has been specified. This command is not executed."""))
        spss.EndProcedure()
    elif len(varnames) < 2:
        spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
        table = spss.BasePivotTable("Warnings ","Warnings")
        table.Append(spss.Dimension.Place.row,"rowdim",hideLabels=True)
        rowLabel = CellText.String("1")
        table[(rowLabel,)] = CellText.String(_("""At least two variables must be specified. This command is not executed."""))
        spss.EndProcedure()
        
    else:
        try:
            warntext = []
            if cilevel < 50:
                warntext.append(_("CILEVEL cannot be less than 50%. It has been reset to 50%."))
                cilevel = 50
            if cilevel > 99.999:
                warntext.append(_("CILEVEL cannot be greater than 99.999%. It has been reset to 99.999%."))
                cilevel = 99.999
            if cilevel == int(cilevel):
                cilevel = int(cilevel)
            varlist = varnames[0]
            for i in range(1,len(varnames)):
                varlist = varlist + ' ' + varnames[i]
            spss.Submit("PRESERVE.")
            tempdir = tempfile.gettempdir()
            spss.Submit("""CD "%s".""" % tempdir)
            wtvar = spss.GetWeightVar()
            if wtvar != None:
                spss.Submit(r"""
COMPUTE %s=RND(%s).""" % (wtvar, wtvar))
                spss.Submit(r"""
EXECUTE.""")
                wtdn = GetWeightSum(varnames)
            else:
                wtdn = spss.GetCaseCount()
            maxloops = wtdn + 1
            spss.Submit("""SET PRINTBACK=OFF MPRINT=OFF OATTRS=ENG MXLOOPS=%s.""" % maxloops)
            activeds = spss.ActiveDataset()
            if activeds == "*":
                activeds = "D" + str(random.uniform(.1,1))
                spss.Submit("DATASET NAME %s" % activeds)
            tmpvar1 = "V" + str(random.uniform(.1,1))
            tmpvar2 = "V" + str(random.uniform(.1,1))
            tmpvar3 = "V" + str(random.uniform(.1,1))
            tmpfile1 = "F" + str(random.uniform(.1,1))
            tmpfile2 = "F" + str(random.uniform(.1,1))
            tmpdata1 = "D" + str(random.uniform(.1,1))
            tmpdata2 = "D" + str(random.uniform(.1,1))
            tmpdata3 = "D" + str(random.uniform(.1,1))
            omstag1 = "T" + str(random.uniform(.1,1))
            omstag2 = "T" + str(random.uniform(.1,1))
            omstag3 = "T" + str(random.uniform(.1,1))
            omstag4 = "T" + str(random.uniform(.1,1))
            omstag5 = "T" + str(random.uniform(.1,1))
            omstag6 = "T" + str(random.uniform(.1,1))
            lowlabel = _("""Lower %s%% Asymptotic CI Bound""") % cilevel
            upplabel = _("""Upper %s%% Asymptotic CI Bound""") % cilevel
            spss.Submit(r"""
DATASET COPY %s WINDOW=HIDDEN.""" % tmpdata1)
            spss.Submit(r"""
DATASET ACTIVATE %s WINDOW=ASIS.""" % tmpdata1)
            filt = spssaux.GetSHOW("FILTER", olang="english")
            if filt != "No case filter is in effect":
                filtcond = filt.strip("(FILTER)")
                select = "SELECT IF " + str(filtcond) + "."
                spss.Submit("""%s""" % select)
                spss.Submit("""EXECUTE.""")
                spss.Submit("""USE ALL.""")
            banana = spssaux.getDatasetInfo(Info="SplitFile")
            if banana != "":
                warntext.append(_("This command ignores split file status."))
                spss.Submit(r"""SPLIT FILE OFF.""")   
            spss.Submit(r"""
COUNT %s=%s (MISSING).""" % (tmpvar1, varlist))
            spss.Submit(r"""
SELECT IF %s=0.""" % tmpvar1)
            spss.Submit(r"""
EXECUTE.
MISSING VALUES ALL ().""")
            validn=spss.GetCaseCount()
            if wtvar == None:
                spss.Submit(r"""
SAVE OUTFILE=%s.""" % tmpfile1)
            else:
                spss.Submit(r"""
DO IF %s >= 1.""" % wtvar)
                spss.Submit(r"""
+ LOOP #i=1 TO %s.""" % wtvar)
                spss.Submit(r"""
XSAVE OUTFILE=%s
  /KEEP=%s
  /DROP=%s.""" % (tmpfile1, varlist, wtvar))
                spss.Submit(r"""
+ END LOOP.
END IF.
EXECUTE.
""")   
            spss.Submit(r"""
OMS /SELECT ALL EXCEPT=WARNINGS 
 /IF COMMANDS=['Variables to Cases'] 
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag1)
            spss.Submit(r"""
VARSTOCASES
  /MAKE %s FROM %s.""" % (tmpvar2, varlist))
            spss.Submit(r"""
OMSEND TAG = ['"%s"'].""" % omstag1)
            catdata = []
            try:
                cur = spss.Cursor(isBinary=False)
            except:
                cur = spss.Cursor()
            while True:
                datarow = cur.fetchone()
                if datarow is None:
                    break
                catdata.append(datarow[-1])
            cur.close()
            cats = list(set(catdata))
            ncats = len(cats)
            nraters = len(varnames)
            neededn = max(ncats, nraters)
            if validn < neededn:
                spss.Submit(r"""
OMS
 /SELECT TABLES
 /IF COMMANDS=['Fleiss Kappa'] SUBTYPES=['Notes']
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag2)
                spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
                table = spss.BasePivotTable("Warnings ","Warnings")
                table.Append(spss.Dimension.Place.row,"rowdim",hideLabels=True)
                rowLabel = CellText.String("1")
                table[(rowLabel,)] = CellText.String(_("""There are too few complete cases. This command is not executed."""))
                spss.EndProcedure()
                spss.Submit(r"""
OMSEND TAG = ['"%s"'].""" % omstag2)
            elif ncats < 2:
                spss.Submit(r"""
OMS
 /SELECT TABLES
 /IF COMMANDS=['Fleiss Kappa'] SUBTYPES=['Notes']
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag2)
                spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
                table = spss.BasePivotTable("Warnings ","Warnings")
                table.Append(spss.Dimension.Place.row,"rowdim",hideLabels=True)
                rowLabel = CellText.String("1")
                table[(rowLabel,)] = CellText.String(_("""All ratings are the same. This command is not executed."""))
                spss.EndProcedure()
                spss.Submit(r"""
OMSEND TAG = ['"%s"'].""" % omstag2)
            else:
                if len(warntext) > 0:
                    spss.Submit(r"""
OMS
 /SELECT TABLES
 /IF COMMANDS=['Fleiss Kappa'] SUBTYPES=['Notes']
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag2)
                    if len(warntext) == 1:
                        spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
                        table = spss.BasePivotTable("Warnings ","Warnings")
                        table.Append(spss.Dimension.Place.row,"rowdim",hideLabels=True)
                        rowLabel = CellText.String("1")
                        table[(rowLabel,)] = CellText.String("%s" % warntext[0])
                        spss.EndProcedure()
                    if len(warntext) == 2:
                        spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
                        table = spss.BasePivotTable("Warnings ","Warnings")
                        table.Append(spss.Dimension.Place.row,"rowdim",hideLabels=True)
                        rowLabel = CellText.String("1")
                        table[(rowLabel,)] = CellText.String("%s \n" "%s" % (warntext[0], warntext[1]))
                        spss.EndProcedure()
                    spss.Submit(r"""
OMSEND TAG = ['"%s"'].""" % omstag2)
                spss.Submit(r"""
AGGREGATE
  /OUTFILE=%s
  /BREAK=%s
  /%s=N.""" % (tmpfile2, tmpvar2, tmpvar3))
                spss.Submit(r"""
DATASET DECLARE %s WINDOW=HIDDEN.""" % tmpdata2)
                spss.Submit(r"""
DATASET DECLARE %s WINDOW=HIDDEN.""" % tmpdata3)
                spss.Submit(r"""
OMS /SELECT ALL EXCEPT=WARNINGS 
 /IF COMMANDS=['Matrix'] 
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag3)
                spss.Submit(r"""
MATRIX.
GET x 
  /FILE=%s
  /VARIABLES=%s.
GET ratecats
  /FILE=%s
  /VARIABLES=%s.
COMPUTE n=NROW(x).
COMPUTE c=NROW(ratecats).
COMPUTE y=MAKE(n,c,0).
LOOP i=1 to n.
+ LOOP j=1 to NCOL(x).
+   LOOP k=1 to c.
+     DO IF x(i,j)=ratecats(k).
+       COMPUTE y(i,k)=y(i,k)+1.
+     END IF.
+   END LOOP.
+ END LOOP.
END LOOP.
COMPUTE k=NCOL(x).
COMPUTE pe=MSUM((CSUM(y)/MSUM(y))&**2).
COMPUTE pa=MSSQ(y)/(NROW(y)*k*(k-1))-(1/(k-1)).
COMPUTE kstat=(pa-pe)/(1-pe).
COMPUTE cp=(CSSQ(y)-CSUM(y))&/((k-1)&*CSUM(y)).
COMPUTE pj=CSUM(y)/MSUM(y).
COMPUTE one=MAKE(1,NCOL(pj),1).
COMPUTE qj=one-pj.
COMPUTE kj=(cp-pj)&/qj.
COMPUTE num=2*((pj*t(qj))**2-MSUM(pj&*qj&*(qj-pj))).
COMPUTE den=n*k*(k-1)*((pj*t(qj))**2).
COMPUTE ase=SQRT(num/den).
COMPUTE z=kstat/ase.
COMPUTE sig=1-CHICDF(z**2,1).
SAVE {kstat,ase,z,sig}
   /OUTFILE=%s
   /VARIABLES=kstat,ase,z,sig.
COMPUTE asej=MAKE(1,c,SQRT(2/(n*k*(k-1)))).
COMPUTE zj=kj&/asej.
COMPUTE sigj=one-CHICDF(zj&**2,1).
SAVE {ratecats,t(cp),t(kj),t(asej),t(zj),t(sigj)}
  /OUTFILE=%s
  /VARIABLES=category,cp,kstat,ase,z,sig.
END MATRIX.""" % (tmpfile1, varlist, tmpfile2, tmpvar2, tmpdata2, tmpdata3))
                spss.Submit(r"""
OMSEND TAG = ['"%s"'].""" % omstag3)
                spss.Submit(r"""
DATASET ACTIVATE %s WINDOW=ASIS.""" % tmpdata2)
                spss.Submit(r"""
COMPUTE lower=kstat-SQRT(IDF.CHISQUARE(%s/100,1))*ase.""" % cilevel)
                spss.Submit(r"""
COMPUTE upper=kstat+SQRT(IDF.CHISQUARE(%s/100,1))*ase.""" % cilevel)
                spss.Submit(r"""
FORMATS kstat ase z sig lower upper (F11.3).
VARIABLE LABELS kstat %s. """ % _smartquote(_("""Kappa""")))
                spss.Submit(r"""
VARIABLE LABELS ase %s. """ % _smartquote(_("""Asymptotic Standard Error""")))
                spss.Submit(r"""
VARIABLE LABELS z %s. """ % _smartquote(_("""Z""")))
                spss.Submit(r"""
VARIABLE LABELS sig %s. """ % _smartquote(_("""P Value""")))
                spss.Submit(r"""
VARIABLE LABELS lower %s. """ % _smartquote(_(lowlabel)))
                spss.Submit(r"""
VARIABLE LABELS upper %s. """ % _smartquote(_(upplabel)))
                spss.Submit(r"""
EXECUTE.
""")
                try:
	                cur = spss.Cursor(isBinary=False)
                except:
	                cur = spss.Cursor()
                data1=cur.fetchone()
                cur.close()
                collabels1=[spss.GetVariableLabel(0),spss.GetVariableLabel(1),spss.GetVariableLabel(2),spss.GetVariableLabel(3), \
                                         spss.GetVariableLabel(4),spss.GetVariableLabel(5)]
                celldata1=[data1[0],data1[1],data1[2],data1[3],data1[4],data1[5]]
                spss.Submit(r"""
DATASET ACTIVATE %s WINDOW=ASIS.""" % tmpdata3)
                spss.Submit(r"""
COMPUTE lower=kstat-SQRT(IDF.CHISQUARE(%s/100,1))*ase.""" % cilevel)
                spss.Submit(r"""
COMPUTE upper=kstat+SQRT(IDF.CHISQUARE(%s/100,1))*ase.""" % cilevel)
                spss.Submit(r"""
FORMATS category (F10.0) cp kstat ase z sig lower upper (F11.3).
VARIABLE LABELS category %s. """ % _smartquote(_("""Rating Category""")))
                spss.Submit(r"""
VARIABLE LABELS cp %s. """ % _smartquote(_("""Conditional Probability""")))
                spss.Submit(r"""
VARIABLE LABELS kstat %s. """ % _smartquote(_("""Kappa""")))
                spss.Submit(r"""
VARIABLE LABELS ase %s. """ % _smartquote(_("""Asymptotic Standard Error""")))
                spss.Submit(r"""                
VARIABLE LABELS z %s. """ % _smartquote(_("""Z""")))
                spss.Submit(r""" 
VARIABLE LABELS sig %s. """ % _smartquote(_("""P Value""")))
                spss.Submit(r"""
VARIABLE LABELS lower %s. """ % _smartquote(_(lowlabel)))
                spss.Submit(r"""
VARIABLE LABELS upper %s. """ % _smartquote(_(upplabel)))
                spss.Submit(r""" 
EXECUTE.""")
                spss.Submit(r"""
OMS
 /SELECT TABLES
 /IF COMMANDS=['Fleiss Kappa'] SUBTYPES=['Notes']
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag4)
                spss.Submit(r"""
OMS
 /SELECT TEXTS
 /IF COMMANDS=['Fleiss Kappa'] LABELS=['Active Dataset']
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag5)
                if len(warntext) > 0:
                    spss.Submit(r"""
OMS
 /SELECT HEADINGS
 /IF COMMANDS=['Fleiss Kappa']
 /DESTINATION VIEWER=NO
 /TAG = '"%s"'.""" % omstag6)
                n=spss.GetCaseCount
                rlabels=[]
                data2=[]
                try:
                    cur = spss.Cursor(isBinary=False)
                except:
                    cur = spss.Cursor()
                for i in range(0,spss.GetCaseCount()):
                    datarow=cur.fetchone()
                    data2.append(datarow[1:])
                    rlabels.append(datarow[0])
                cur.close()
                def _flatten(seq):
                    for item in seq:
                        if spssaux._isseq(item):
                            for subitem in _flatten(item):
                                yield subitem
                        else:
                            yield item
                data2=[item for item in _flatten(data2)]
                spss.StartProcedure(_("Fleiss Kappa"),"Fleiss Kappa")
                table1 = spss.BasePivotTable(_("Overall Kappa"),"Overall Kappa")
                table1.SimplePivotTable(rowdim = _(""),
                       rowlabels=[CellText.String("Overall")],
                       coldim="",
                       collabels=collabels1,
                       cells=celldata1)
                if any(item != round(item) for item in rlabels):
                    caption=(_("Non-integer rating category values are truncated for presentation."))
                else:
                    caption=("")
                table2=spss.BasePivotTable(_("Kappas for Individual Categories"),
                                _("Individual Category Kappa Statistics"),caption=caption)
                rowlabels=[(CellText.String("{:>9.0f}".format(rlabels[i]))) for i in range(len(rlabels))]
                collabels=[spss.GetVariableLabel(1),spss.GetVariableLabel(2),spss.GetVariableLabel(3), \
                      spss.GetVariableLabel(4),spss.GetVariableLabel(5),spss.GetVariableLabel(6), \
                      spss.GetVariableLabel(7)]
                table2.SimplePivotTable(rowdim=_("  Rating Category"),
                      rowlabels=rowlabels,
                      coldim="",
                      collabels=collabels,
                      cells=data2)
                spss.EndProcedure()
                if len(warntext) > 0:
                    spss.Submit(r"""
OMSEND TAG = ['"%s"'].""" % omstag6)
        finally:
            try:
                spss.Submit("""
DATASET CLOSE %s.""" % tmpdata1)
                spss.Submit(r"""
DATASET ACTIVATE %s WINDOW=ASIS.""" % activeds)
                if validn >= neededn:
                    if ncats >= 2:
                        spss.Submit("""
OMSEND TAG=['"%s"' '"%s"'].""" % (omstag4,omstag5))
                        spss.Submit("""
DATASET CLOSE %s.""" % tmpdata2)
                        spss.Submit("""
DATASET CLOSE %s.""" % tmpdata3)
                        spss.Submit("""
ERASE FILE=%s.""" % tmpfile1)
                        spss.Submit(r"""
ERASE FILE=%s.""" % tmpfile2)
            except:
                pass
            spss.Submit("""
RESTORE.
""")
